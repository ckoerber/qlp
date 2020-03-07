import numpy as np
import pandas as pd
import hashlib
from qlpdb.graph.models import Graph as graph_Graph
from qlpdb.experiment.models import Experiment as experiment_Experiment
from qlpdb.data.models import Data as data_Data

from minorminer import find_embedding
from dwave.system.composites import EmbeddingComposite, FixedEmbeddingComposite


class AnnealOffset:
    def __init__(self, tag):
        self.tag = tag

    def fcn(self, h, min_offset, max_offset):
        if self.tag == "constant":
            return np.zeros(len(h)), f"Constant"
        if self.tag == "linear":
            hnorm = abs(h) / max(abs(h))
            return hnorm * (max_offset - min_offset) * 0.9 + min_offset * 1.1, f"Linear"
        if self.tag == "signedlinear":
            hnorm = 0.5*(1.0+ h / max(abs(h)))
            return hnorm * (max_offset - min_offset) * 0.9 + min_offset * 1.1, f"Signedlinear"
        if self.tag == "negsignedlinear":
            hnorm = 0.5*(1.0- h / max(abs(h)))
            return hnorm * (max_offset - min_offset) * 0.9 + min_offset * 1.1, f"Negsignedlinear"
        else:
            print(
                "Anneal offset not defined.\nDefine in AnnealOffset class inside qlp.mds.mds_qlpdb"
            )


def retry_embedding(sampler, qubo_dict, qpu_graph, n_tries):
    for i in range(n_tries):
        try:
            embedding = find_embedding(qubo_dict, qpu_graph)
            embedding_idx = [
                idx for embed_list in embedding.values() for idx in embed_list
            ]
            embed = FixedEmbeddingComposite(sampler, embedding)
            anneal_offset_ranges = np.array(
                embed.properties["child_properties"]["anneal_offset_ranges"]
            )
            min_offset = max(
                [offsets[0] for offsets in anneal_offset_ranges[embedding_idx]]
            )
            max_offset = min(
                [offsets[1] for offsets in anneal_offset_ranges[embedding_idx]]
            )
            if max_offset - min_offset < 0.1:
                raise ValueError(
                    f"\n{max_offset - min_offset}Not enough offset range for inhomogeneous driving. Try another embedding."
                )
            else:
                return embed, embedding, min_offset, max_offset
        except Exception as e:
            print(e)
            continue


def find_offset(h, fcn, embedding, min_offset, max_offset):
    anneal_offset = np.zeros(2048)  # expects full yield 2000Q
    offset_value, tag = fcn(h, min_offset, max_offset)
    for logical_qubit, qubit in embedding.items():
        for idx in qubit:
            # sets same offset for all qubits in chain
            anneal_offset[idx] = offset_value[logical_qubit]
    return list(anneal_offset), tag


def insert_result(graph_params, experiment_params, data_params):
    # select or insert row in graph
    graph, created = graph_Graph.objects.get_or_create(
        tag=graph_params["tag"],  # Tag for graph type (e.g. Hamming(n,m) or K(n,m))
        total_vertices=graph_params[
            "total_vertices"
        ],  # Total number of vertices in graph
        total_edges=graph_params["total_edges"],  # Total number of edges in graph
        max_edges=graph_params["max_edges"],  # Maximum number of edges per vertex
        adjacency=graph_params[
            "adjacency"
        ],  # Sorted adjacency matrix of dimension [N, 2]
        adjacency_hash=graph_params[
            "adjacency_hash"
        ],  # md5 hash of adjacency list used for unique constraint
    )

    # select or insert row in experiment
    experiment, created = experiment_Experiment.objects.get_or_create(
        graph=graph,  # Foreign Key to `graph`
        machine=experiment_params["machine"],  # Hardware name (e.g. DW_2000Q_5)
        settings=experiment_params["settings"],  # Store DWave machine parameters
        settings_hash=experiment_params[
            "settings_hash"
        ],  # md5 hash of key sorted settings
        p=experiment_params["p"],  # Coefficient of penalty term, 0 to 9999.99
        chain_strength=experiment_params["chain_strength"],
        tag=experiment_params["tag"],
    )

    # select or insert row in data
    for idx in range(len(data_params["spin_config"])):
        measurement = data_Data.objects.filter(experiment=experiment).order_by(
            "-measurement"
        )
        if measurement.exists():
            measurement = measurement.first().measurement + 1
        else:
            measurement = 0
        data, created = data_Data.objects.get_or_create(
            experiment=experiment,  # Foreign Key to `experiment`
            measurement=measurement,  # Increasing integer field labeling measurement number
            spin_config=list(
                data_params["spin_config"][idx]
            ),  # Spin configuration of solution, limited to 0, 1
            chain_break_fraction=data_params["chain_break_fraction"][idx],
            energy=data_params["energy"][
                idx
            ],  # Energy corresponding to spin_config and QUBO
            constraint_satisfaction=data_params["constraint_satisfaction"][idx],
        )
    return data


def graph_summary(tag, graph, qubo):
    """
    Get summary statistics of input graph
    :param graph:
    :return:
    """
    vertices = np.unique(np.array([i for i in graph]).flatten())
    neighbors = {v: 0 for v in vertices}
    for i in graph:
        neighbors[i[0]] += 1
        neighbors[i[1]] += 1
    params = dict()
    params["tag"] = tag
    params["total_vertices"] = len(vertices)
    params["total_edges"] = len(graph)
    params["total_qubits"] = len(qubo.todense())
    params["max_edges"] = max(neighbors.values())
    params["adjacency"] = [list(i) for i in list(graph)]
    params["adjacency_hash"] = hashlib.md5(
        str(np.sort(list(graph))).replace(" ", "").encode("utf-8")
    ).hexdigest()
    return params


def experiment_summary(machine, settings, penalty, chain_strength, tag):
    params = dict()
    params["machine"] = machine
    params["settings"] = {
        key: settings[key] for key in settings if key not in ["anneal_offsets"]
    }
    params["p"] = penalty
    params["chain_strength"] = chain_strength
    params["tag"] = tag
    params["settings_hash"] = hashlib.md5(
        str([[key, params["settings"][key]] for key in sorted(params["settings"])])
        .replace(" ", "")
        .encode("utf-8")
    ).hexdigest()
    return params


def data_summary(raw, graph_params, experiment_params):
    params = dict()
    params["spin_config"] = raw.iloc[:, : graph_params["total_qubits"]].values
    params["energy"] = (
        raw["energy"].values + experiment_params["p"] * graph_params["total_vertices"]
    )
    params["chain_break_fraction"] = raw["chain_break_fraction"].values
    params["constraint_satisfaction"] = np.equal(
        params["energy"],
        np.sum(params["spin_config"][:, : graph_params["total_vertices"]], axis=1),
    )
    return params


def QUBO_to_Ising(Q):
    q = np.diagonal(Q)
    QD = np.copy(Q)
    for i in range(len(QD)):
        QD[i, i] = 0.0
    QQ = np.copy(QD + np.transpose(QD))
    J = np.triu(QQ) / 4.0
    uno = np.ones(len(QQ))
    h = q / 2 + np.dot(QQ, uno) / 4
    g = np.dot(uno, np.dot(QD, uno)) / 4.0 + np.dot(q, uno) / 2.0
    return (J, h, g)

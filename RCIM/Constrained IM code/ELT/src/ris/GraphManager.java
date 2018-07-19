package ris;

import static ris.Loader.NUM_NODES;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Random;

public final class GraphManager {

	private static List<int[]> EDGES;

	private GraphManager() {
	}

	public static void setEdges(Map<Integer, List<Integer>> edgeMap) {
		EDGES = new ArrayList<>(NUM_NODES);
		for (int i = 0; i < NUM_NODES; i++) {
			EDGES.add(edgeMap.get(i).stream().mapToInt(j -> j).toArray());
		}
	}

	public static int[] generateRRSet(Random random) {
		int[] RR = new int[NUM_NODES];
		int rrCounter = 0;
		boolean[] visited = new boolean[NUM_NODES];
		int s = random.nextInt(NUM_NODES);
		visited[s] = true;
		RR[rrCounter++] = s;
		while (true) {
			int[] srcs = EDGES.get(s);
			if (srcs.length == 0) {
				break;
			}
			s = srcs[random.nextInt(srcs.length)];
			if (visited[s]) {
				break;
			}
			visited[s] = true;
			RR[rrCounter++] = s;
		}
		return Arrays.copyOf(RR, rrCounter);
	}
}

/**
 * 
 */
package ris;

import static ris.E.NUM_SAMPLES;
import static ris.E.NUM_THREADS;
import static ris.Worker.PROTECTED;
import static ris.Worker.SEEDS;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * @author shay
 *
 */
public class Loader {
	public static String RESOURCES_PATH;
	private static String IM_PATH;
	public static String OUTPUT_PATH;
	public static int NUM_NODES;
	public static int NUM_EDGES;
	private static int NUM_FEATURES;
	private static String[] PROTECTED_CRITERIA;

	private Loader() {
	}

	public static void init() {
		loadParams();
		loadProtected();
		loadEdges();
	}

	private static void loadEdges() {
		String edgesPath = IM_PATH + File.separator + "graph.txt";
		Path path = Paths.get(edgesPath);
		Map<Integer, List<Integer>> edgeMap = new HashMap<>(NUM_NODES);
		for (int i = 0; i < NUM_NODES; i++) {
			edgeMap.put(i, new ArrayList<>());
		}
		try (Stream<String> lines = Files.lines(path)) {
			lines.map(line -> line.split("\t")).forEach(parts -> {
				int src = Integer.valueOf(parts[0]);
				int dst = Integer.valueOf(parts[1]);
				edgeMap.get(dst).add(src);
			});
		} catch (IOException ex) {
			System.err.println("Error opening file " + edgesPath);
			System.err.println(ex.getMessage());
		}
		GraphManager.setEdges(edgeMap);
		
	}

	private static void loadParams() {
		IM_PATH = RESOURCES_PATH + File.separator + "IM";
		OUTPUT_PATH = RESOURCES_PATH + File.separator + "OUTPUT";
		Path paramsPath = Paths.get(IM_PATH + File.separator + "params.txt");
		List<String> lines;
		Map<String, String> params = new HashMap<>();
		try {
			lines = Files.readAllLines(paramsPath);
			Consumer<String> addEntry = l -> {
				if (l.indexOf("=") != -1) {
					String[] parts = l.split("=");
					String k = parts[0];
					String v = parts[1].trim();
					params.put(k, v);
				}
			};
			lines.stream().forEach(addEntry);
			NUM_NODES = Integer.parseInt(params.get("n"));
			NUM_EDGES = Integer.parseInt(params.get("m"));
			NUM_SAMPLES = Integer.parseInt(params.get("num_samples"));
			NUM_FEATURES = Integer.parseInt(params.get("num_features"));
			PROTECTED_CRITERIA = params.get("protected_criteria").split("\t");
			NUM_THREADS = Integer.parseInt(params.get("num_threads"));
			SEEDS = parseSeeds(params.get("seeds"));

		} catch (IOException e) {
			System.err.println("ERROR reading params file!");
			System.err.println("Given RESOURCES_PATH: " + RESOURCES_PATH);
			System.err.println(e.getMessage());
			e.printStackTrace();
			System.exit(-1);
		}
	}

	
	private static List<Integer> parseSeeds(String seedsStr) {
		return Arrays.stream(seedsStr.split(", ")).map(s -> Integer.parseInt(s)).collect(Collectors.toList());
	}

	private static void loadProtected() {
		initProtected(loadFeatures());
	}

	private static void initProtected(List<String[]> features) {
		List<Integer> prot = new ArrayList<>();
		for (int i = 0; i < features.size(); i++) {
			String[] feats = features.get(i);
			boolean isMatch = true;
			for (int j = 0; j < NUM_FEATURES; j++) {
				if (!matchCondition(feats[j], PROTECTED_CRITERIA[j].trim())) {
					isMatch = false;
					continue;
				}
			}
			if (isMatch) {
				prot.add(i);
			}
		}
		System.out.println("Number of protected: " + prot.size());
		PROTECTED = prot.stream().mapToInt(i -> i).toArray();
	}

	private static boolean matchCondition(String feature, String condition) {
		if (condition.equals("null")) { // no criteria case
			return true;
		}
		if (condition.indexOf("|") != -1) { // OR case
			String[] conds = condition.split("|");
			for (String cond : conds) {
				if (cond.equals(feature)) {
					return true;
				}
			}
			return false;
		}
		if (condition.startsWith("[") && condition.endsWith("]")) { // range case
			int feat = Integer.parseInt(feature);
			String[] limits = condition.substring(1, condition.length() - 1).split(",");
			String lower = limits[0];
			String upper = limits[1];
			if (lower.equals("null")) {
				return (feat <= Integer.parseInt(upper));
			}
			if (upper.equals("null")) {
				return (feat >= Integer.parseInt(lower));
			}
			return ((feat <= Integer.parseInt(upper)) && (feat >= Integer.parseInt(lower)));
		}
		return feature.equals(condition); // simple case

	}

	private static List<String[]> loadFeatures() {
		String nodesPath = IM_PATH + File.separator + "nodes.txt";
		Path path = Paths.get(nodesPath);
		List<String[]> features = new ArrayList<>(NUM_NODES);
		try (Stream<String> lines = Files.lines(path)) {
			lines.map(line -> line.split("\t")).forEach(parts -> {
				String[] feats = new String[NUM_FEATURES];
				for (int i = 0; i < NUM_FEATURES; i++) {
					feats[i] = parts[i + 1];
				}
				features.add(Integer.parseInt(parts[0]), feats);
			});
		} catch (IOException ex) {
			System.err.println("Error opening file " + nodesPath);
			System.err.println(ex.getMessage());
			System.err.println(ex.getStackTrace());
		}
		return features;
	}

}

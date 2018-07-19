package ris;

import static ris.Loader.NUM_NODES;
import static ris.Loader.OUTPUT_PATH;

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.atomic.AtomicInteger;

public class LPHandler {
	public static final AtomicInteger sampleCounter = new AtomicInteger(0);
	public static int B;
	public static int K;
	public static double T;
	public static int[][] MC;
	public static int[][] PROT_MC;
	private static boolean[] appeared = new boolean[NUM_NODES]; // array indicating which nodes were visited
	private static final AtomicInteger protCounter = new AtomicInteger(0);
	private static final AtomicInteger nonCounter = new AtomicInteger(0);
	public static int NUM_PROTECTED;

	public static void addRR(int[] RR, boolean prot) {
		if (prot) {
			int index = protCounter.getAndIncrement();
			PROT_MC[index] = RR;
		} else {
			int index = nonCounter.getAndIncrement();
			MC[index] = RR;
		}
	}

	private static void fillAppeared() {
		for (int i = 0; i < nonCounter.get(); i++) {
			for (int j : MC[i]) {
				appeared[j] = true;
			}
		}
		for (int i = 0; i < protCounter.get(); i++) {
			for (int j : PROT_MC[i]) {
				appeared[j] = true;
			}
		}
	}

	// size-oriented
	public static void saveLPFormat() {
		fillAppeared(); // fill array indicating which nodes were ever visited

		String xStr = getXSumStr();
		String yStr = getYSumStr();
		String zStr = getZSumStr();
		StringBuilder line;
		
		double threshold = (T * B * protCounter.get()) / NUM_PROTECTED;
		String rhs = String.format("%.10f", threshold);
		System.out.println("regular samples: " + nonCounter.get());
		System.out.println("protected samples: " + protCounter.get());

		Path path = Paths.get(OUTPUT_PATH + File.separator + "ris.lp");
		try (BufferedWriter writer = Files.newBufferedWriter(path, Charset.forName("UTF-8"))) {

			// objective
			writer.write("Maximize" + "\n");
			writer.write(yStr + " + " + zStr + "\n");
			writer.write("Subject To" + "\n");

			// cardinality constraint
			writer.write(xStr + " = " + K + "\n");

			// (protected) size constraint
			writer.write(yStr + " >= " + rhs + "\n");

			// coverage constraints: protected
			for (int i = 0; i < protCounter.get(); i++) {
				line = new StringBuilder();
				for (int node : PROT_MC[i]) {
					line.append("1 x" + Integer.toString(node) + " + ");
				}
				int len = line.length();
				line = new StringBuilder(line.substring(0, len - 2) + "- 1 y" + Integer.toString(i) + " >= 0\n");
				writer.write(line.toString());
			}

			// coverage constraints: non-protected
			for (int i = 0; i < nonCounter.get(); i++) {
				line = new StringBuilder();
				for (int node : MC[i]) {
					line.append("1 x" + Integer.toString(node) + " + ");
				}
				int len = line.length();
				line = new StringBuilder(line.substring(0, len - 2) + "- 1 z" + Integer.toString(i) + " >= 0\n");
				writer.write(line.toString());
			}

			// Bounds
			writer.write("Bounds" + "\n");
			for (int i = 0; i < NUM_NODES; i++) {
				if (appeared[i]) {
					writer.write("x" + Integer.toString(i) + " <= 1\n");
				}
			}
			for (int i = 0; i < protCounter.get(); i++) {
				writer.write("y" + Integer.toString(i) + " <= 1\n");
			}
			for (int i = 0; i < nonCounter.get(); i++) {
				writer.write("z" + Integer.toString(i) + " <= 1\n");
			}
		} catch (IOException ex) {
			ex.printStackTrace();
		}
	}

	private static String getXSumStr() {
		int first = getFirstAppearedIndex();
		StringBuilder line = new StringBuilder("1 x" + Integer.toString(first));
		for (int i = first + 1; i < NUM_NODES; i++) {
			if (appeared[i]) {
				line.append(" + 1 x" + Integer.toString(i));
			}
		}
		return line.toString();
	}

	private static String getYSumStr() {
		StringBuilder line = new StringBuilder("1 y0");
		for (int i = 1; i < protCounter.get(); i++) {
			line.append(" + 1 y" + Integer.toString(i));
		}
		return line.toString();
	}

	private static String getZSumStr() {
		StringBuilder line = new StringBuilder("1 z0");
		for (int i = 1; i < nonCounter.get(); i++) {
			line.append(" + 1 z" + Integer.toString(i));
		}
		return line.toString();
	}

	private static int getFirstAppearedIndex() {
		for (int i = 0; i < appeared.length; i++) {
			if (appeared[i]) {
				return i;
			}
		}
		throw new RuntimeException("Error! No nodes appeared!");
	}



}

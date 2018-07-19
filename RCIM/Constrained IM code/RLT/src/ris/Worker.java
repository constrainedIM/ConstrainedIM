package ris;

import static ris.LPHandler.sampleCounter;
import static ris.R.NUM_SAMPLES;

import java.util.Arrays;
import java.util.Random;

public class Worker implements Runnable {
	public static int[] PROTECTED;
	private static final Random random = new Random();

	public Worker() {
	}

	@Override
	public void run() {
		boolean isSeedProt;
		for (int i = sampleCounter.getAndIncrement(); i < NUM_SAMPLES; i = sampleCounter.getAndIncrement()) {
			int[] RR = GraphManager.generateRRSet(random);
			isSeedProt = false;
			if (Arrays.binarySearch(PROTECTED, RR[0]) >= 0) {
				isSeedProt = true;
			}
			LPHandler.addRR(RR, isSeedProt);
		}
	}
}

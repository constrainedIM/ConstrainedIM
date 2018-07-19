package ris;

import static ris.E.NUM_PROTECTED_SAMPLES;
import static ris.E.NUM_SAMPLES;
import static ris.E.PROTECTED_SUM_INTERSECTIONS;
import static ris.E.SUM_INTERSECTIONS;
import static ris.E.ai;

import java.util.Arrays;
import java.util.List;
import java.util.Random;
public class Worker implements Runnable {
	public static int[] PROTECTED;
	public static List<Integer> SEEDS;
	private static final Random random = new Random();

	public Worker() {
	}

	@Override
	public void run() {
		int intersectionCounter = 0;
		int protIntersectioncounter = 0;
		int protSamplesCounter = 0;
		boolean isSeedProt;
		for (int i = ai.getAndIncrement(); i < NUM_SAMPLES; i = ai.getAndIncrement()) {
			int[] RR = GraphManager.generateRRSet(random);
			// System.out.println(Arrays.toString(RR));
			isSeedProt = false;
			if (Arrays.binarySearch(PROTECTED, RR[0]) >= 0) {
				isSeedProt = true;
				protSamplesCounter++;
			}
			for (int node : RR) {
				if (SEEDS.contains(node)) {
					intersectionCounter++;
					if (isSeedProt) {
						protIntersectioncounter++;
					}
					break;
				}
			}
		}
		SUM_INTERSECTIONS.addAndGet(intersectionCounter);
		NUM_PROTECTED_SAMPLES.addAndGet(protSamplesCounter);
		PROTECTED_SUM_INTERSECTIONS.addAndGet(protIntersectioncounter);
	}

}

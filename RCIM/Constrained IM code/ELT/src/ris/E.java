package ris;

import static ris.Loader.NUM_NODES;
import static ris.Loader.RESOURCES_PATH;
import static ris.Worker.PROTECTED;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;

public class E {

	public static int NUM_THREADS;
	public static int NUM_SAMPLES;
	public static final AtomicInteger ai = new AtomicInteger(0);
	public static final AtomicInteger SUM_INTERSECTIONS = new AtomicInteger(0);
	public static final AtomicInteger PROTECTED_SUM_INTERSECTIONS = new AtomicInteger(0);
	public static final AtomicInteger NUM_PROTECTED_SAMPLES = new AtomicInteger(0);

	public static void main(String[] args) {
		if (args.length != 1) {
			System.err.println("Wrong number of arguments: " + args.length);
			return;
		}
		RESOURCES_PATH = args[0];
		Loader.init();
		long startTime = System.currentTimeMillis();
		E estimator = new E();
		estimator.execute();
		printStats();
		long endTime = System.currentTimeMillis();
		System.out.println("overall time: " + (endTime - startTime) / 1000);
	}

	private static void printStats() {
		double IM = SUM_INTERSECTIONS.get() * (NUM_NODES / (double) NUM_SAMPLES);
		double PIM = PROTECTED_SUM_INTERSECTIONS.get() * (PROTECTED.length / (double) NUM_PROTECTED_SAMPLES.get());
		System.out.println("Estimated influence: " + IM);
		System.out.println("Estimated protected influence: " + PIM);

	}

	public void execute() {
		ai.set(0);
		ExecutorService pool = Executors.newFixedThreadPool(NUM_THREADS);
		List<Future<?>> futures = new ArrayList<>(NUM_THREADS);
		for (int i = 0; i < NUM_THREADS; i++) {
			futures.add(pool.submit(new Worker()));
		}
		for (Future<?> future : futures) {
			try {
				future.get();
			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (ExecutionException e) {
				e.printStackTrace();
			}
		}
		pool.shutdown();
	}
}

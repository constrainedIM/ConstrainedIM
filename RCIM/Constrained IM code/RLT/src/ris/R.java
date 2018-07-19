package ris;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import static ris.Loader.*;

public class R {
	public static int NUM_THREADS;
	public static int NUM_SAMPLES;
	
	public static void main(String[] args) {
		if (args.length != 1) {
			System.err.println("Wrong number of arguments: " + args.length);
			return;
		}
		RESOURCES_PATH = args[0];
		long startTime = System.currentTimeMillis();
		Loader.init();
		
		R risRunner = new R();
		risRunner.execute();	
		
		LPHandler.saveLPFormat();
		
		long endTime = System.currentTimeMillis();
		System.out.println("overall time: " + (endTime - startTime) / 1000);
	}

	public void execute() {
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

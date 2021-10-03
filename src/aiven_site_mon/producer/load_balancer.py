import os, time, signal
import multiprocessing
from aiven_site_mon.common import Logger, timeit

def _init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    multiprocessing.current_process().name = "Worker-{}".format(os.getpid())

class LoadBalancer:
    #modes
    ROUND_ROBIN = 1
    COMPRESSED = 2

    #internal consts
    __MIN_PROCESSES = 1
    __MAX_PROCESSES = 50
    __MIN_PERIOD_SEC = 0.05

    def __init__( self,
                  run_period_sec,
                  worker,
                  worker_data=None,
                  all_results_handler=None,
                  processes=os.cpu_count(),
                  max_working_time_sec=180
                ) -> None:

        if run_period_sec < self.__MIN_PERIOD_SEC:
            run_period_sec = self.__MIN_PERIOD_SEC

        if not callable(worker):
            raise TypeError('worker must be a callable')
        if all_results_handler is not None and not callable(all_results_handler):
            raise TypeError('all_results_handler must be a callable')

        #check & make data iterable
        if not hasattr(worker_data, '__len__'):
            worker_data = list(worker_data)

        if processes < self.__MIN_PROCESSES:
            processes = self.__MIN_PROCESSES
        elif processes > self.__MAX_PROCESSES:
            processes = self.__MAX_PROCESSES

        if max_working_time_sec < 0:
            max_working_time_sec = 0

        self.__run_period_sec       = run_period_sec
        self.__worker               = worker
        self.__worker_data          = worker_data
        self.__all_results_handler  = all_results_handler
        self.__processes            = processes
        self.__max_working_time_sec = max_working_time_sec
        self.__process_pool         = multiprocessing.Pool(self.__processes, initializer=_init_worker)

    def __do_comperessed(self):
        Logger.trace("compressed work started (use {} processes)...".format(self.__processes))
        async_info_it = self.__process_pool.map_async(self.__worker, self.__worker_data)
        try:
            info_it = async_info_it.get(self.__max_working_time_sec)
            if self.__all_results_handler is not None:
                self.__all_results_handler(list(info_it))
        except multiprocessing.TimeoutError:
            Logger.error("Error: Working time is expired!")


    def __do_round_robin(self):
        #TODO implement!
        pass

    @timeit
    def do_work(self):
        start_time = time.time()

        self.__do_comperessed()

        work_duration = time.time() - start_time
        delay = self.__run_period_sec - work_duration
        Logger.info("sleep to {:.3f}".format(delay))

        if delay > 0:
            time.sleep(delay)
        else:
            Logger.warning("Processing takes a long time ({:.3f}sec). Please, increase update period."
                            .format(work_duration))


    def stop(self):
        self.__process_pool.close()
        self.__process_pool.join()

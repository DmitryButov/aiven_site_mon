import os, signal
import multiprocessing
from aiven_site_mon.common import Logger, timeit

def _init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    multiprocessing.current_process().name = "Worker-{}".format(os.getpid())

class LoadBalancer:
    __PROCESSES_MIN = 1
    __PROCESSES_MAX = 50

    def __init__( self,
                  worker,
                  worker_data=None,
                  all_results_handler=None,
                  processes=os.cpu_count(),
                  max_working_time_sec=180
                ) -> None:

        if not callable(worker):
            raise TypeError('worker must be a callable')
        if all_results_handler is not None and not callable(all_results_handler):
            raise TypeError('all_results_handler must be a callable')

        #check & make data iterable
        if not hasattr(worker_data, '__len__'):
            worker_data = list(worker_data)

        if processes < self.__PROCESSES_MIN:
            processes = self.__PROCESSES_MIN
        elif processes > self.__PROCESSES_MAX:
            processes = self.__PROCESSES_MAX

        if max_working_time_sec < 0:
            max_working_time_sec = 0

        self.__worker               = worker
        self.__worker_data          = worker_data
        self.__all_results_handler  = all_results_handler
        self.__processes            = processes
        self.__max_working_time_sec = max_working_time_sec
        self.__process_pool         = multiprocessing.Pool(self.__processes, initializer=_init_worker)


    @timeit
    def do_work(self):
        Logger.trace("parallel work started! (use {} processes)...".format(self.__processes))
        async_info_it = self.__process_pool.map_async(self.__worker, self.__worker_data)
        try:
            info_it = async_info_it.get(self.__max_working_time_sec)
            if self.__all_results_handler is not None:
                self.__all_results_handler(list(info_it))
        except multiprocessing.TimeoutError:
            Logger.error("Error: Working time is expired!")

    def stop(self):
        self.__process_pool.close()
        self.__process_pool.join()

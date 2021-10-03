import os, time, signal
import multiprocessing
from aiven_site_mon.common import Logger, timeit

def _init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    multiprocessing.current_process().name = 'Worker-{}'.format(os.getpid())

class LoadBalancer:

    # Balancing policies:
    #   - ROUND_ROBIN
    #       Jobs are evenly spread over time.
    #       Each job works separately from others at regular update time intervals (run period_sec).
    #       Time spread between starting jobs calculated as run period divided by amount of items in worker_data_list.
    #       CPU load is balanced.
    #   - COMPRESSED
    #       Jobs are compressed in time.
    #       The goal of this policy is to run all jobs (corresponding with items from worker_data_list) together,
    #       in the shortest possible time.
    #       This appoach can be applicable if needed to bind all jobs to some one timepoint.
    #       CPU load is not balanced, it periodically increases to high values on polling timepoints
    ROUND_ROBIN = 'round_robin'
    COMPRESSED = 'compressed'

    # Internal consts
    __MIN_PROCESSES = 1
    __MAX_PROCESSES = 50
    __MIN_PERIOD_SEC = 0.05

    def __init__( self,
                  balancing_policy,
                  run_period_sec,
                  worker,
                  worker_data_list=None,
                  all_results_handler=None,     # use only for compressed policy
                  processes=os.cpu_count(),
                  max_working_time_sec=180
                ) -> None:

        if not callable(worker):
            raise TypeError('worker must be a callable')
        if all_results_handler is not None and not callable(all_results_handler):
            raise TypeError('all_results_handler must be a callable')

        #check & make data iterable
        if not hasattr(worker_data_list, '__len__'):
            worker_data_list = list(worker_data_list)

        if len(worker_data_list) == 0:
            raise ValueError('len of worker_data_list should not be 0')

        if processes < self.__MIN_PROCESSES:
            processes = self.__MIN_PROCESSES
        elif processes > self.__MAX_PROCESSES:
            processes = self.__MAX_PROCESSES

        if max_working_time_sec < 0:
            max_working_time_sec = 0

        if run_period_sec < self.__MIN_PERIOD_SEC:
            run_period_sec = self.__MIN_PERIOD_SEC

        if balancing_policy != self.ROUND_ROBIN and balancing_policy != self.COMPRESSED:
            raise ValueError('wrong balancing policy value')

        if balancing_policy == self.ROUND_ROBIN:
            self.__run_period_sec = run_period_sec / len(worker_data_list)
            self.__balancing_func = self.__do_round_robin
            self.__item_idx = 0
        elif balancing_policy == self.COMPRESSED:
            self.__run_period_sec = run_period_sec
            self.__balancing_func = self.__do_comperessed
        else:
            raise ValueError('wrong balancing policy: {}'.format(balancing_policy))

        self.__worker               = worker
        self.__worker_data_list     = worker_data_list
        self.__all_results_handler  = all_results_handler
        self.__max_working_time_sec = max_working_time_sec
        self.__process_pool         = multiprocessing.Pool(processes, initializer=_init_worker)

        Logger.info('Load Balancer: Use {} balancing policy, use {} processes'.
                     format(balancing_policy, processes))

    def __do_comperessed(self):
        Logger.trace('compressed work started...')
        async_info_it = self.__process_pool.map_async(self.__worker, self.__worker_data_list)
        try:
            info_it = async_info_it.get(self.__max_working_time_sec)
            if self.__all_results_handler is not None:
                self.__all_results_handler(list(info_it))
        except multiprocessing.TimeoutError:
            Logger.error('Error: Working time is expired!')

    def __do_round_robin(self):
        idx = self.__item_idx
        item = self.__worker_data_list[idx]

        Logger.trace('round-robin work started for {}'.format(item))
        self.__process_pool.apply_async(self.__worker, (item, ))

        idx += 1
        if idx == len(self.__worker_data_list):  idx = 0
        self.__item_idx = idx

    @timeit
    def do_work(self):
        start_time = time.time()

        self.__balancing_func()

        work_duration = time.time() - start_time
        delay = self.__run_period_sec - work_duration
        Logger.trace('sleep to {:.3f}'.format(delay))

        if delay > 0:
            time.sleep(delay)
        else:
            Logger.warning('Processing takes a long time ({:.3f}sec). Please, increase update period.'
                            .format(work_duration))


    def stop(self):
        self.__process_pool.close()
        self.__process_pool.join()

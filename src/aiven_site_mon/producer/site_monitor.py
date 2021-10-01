import os, time
from aiven_site_mon.common import Logger

class SiteMonitor:
    UPDATE_MIN_SEC = 1
    PROCESSES_MIN = 1
    PROCESSES_MAX = 50
    MAX_PARSING_TIME_SEC = 180

    def __init__(self, site_list, update_period_sec, processes=os.cpu_count()) -> None:
        self.__site_list = site_list
        self.__update_period_sec = update_period_sec
        self.__processes = processes
        if self.__update_period_sec < self.UPDATE_MIN_SEC: self.__update_period_sec = self.UPDATE_MIN_SEC
        if self.__processes < self.PROCESSES_MIN: self.__processes = self.PROCESSES_MIN
        if self.__processes > self.PROCESSES_MAX: self.__processes = self.PROCESSES_MAX

        #TODO self.__process_pool = multiprocessing.Pool(self.__processes, initializer=init_worker)

    #for debug purposes
    # def __check(self):
    #     info_it = map(check_site_worker, self.__site_list)
    #     for info in list(info_it):
    #          logger.info(info)

    # @timeit
    # def __parallel_check(self):
    #     logger.debug("parallel_check started! (use {} processes)...".format(self.__processes))
    #     try:
    #         async_info_it = self.__process_pool.map_async(check_site_worker, self.__site_list)
    #         info_it = async_info_it.get(self.MAX_PARSING_TIME_SEC)
    #         info_handler(list(info_it))
    #     except multiprocessing.TimeoutError:
    #         logger.error("Error: parsing timeout is achieved!")

    def monitoring(self):
        time.sleep(self.__update_period_sec)
        #self.check()
        #TODO self.__parallel_check()
        Logger.trace("monitoring...")

    def stop(self):
        Logger.info("Monitor stopping...")
        #TODO self.__process_pool.close()
        #TODO self.__process_pool.join()
        Logger.info("Monitor stopped")

import asyncio
from typing import Optional
from loguru import logger

from app.rest_client import make_attempt
from app.solves_pool import get_solve_queue_head, pop_solve_queue_head


class SolveQueueWorker:
    def __init__(self, interval: float = 60):
        self.interval = interval
        self.is_running = False
        self.is_paused = False
        self.task: Optional[asyncio.Task] = None

    async def process_solve_queue_item(self, item: list[str]):
        task_id, flag = item
        response = await make_attempt(task_id, flag)
        # if response['status'] == 'incorrect':
        await pop_solve_queue_head()

    async def worker(self):
        while self.is_running:
            if not self.is_paused:
                try:
                    item = await get_solve_queue_head()
                    if item:
                        await self.process_solve_queue_item(item)
                    else:
                        logger.debug("Solve queue is empty")
                except Exception as e:
                    logger.error(f"Error processing solve queue: {e}")
            
            await asyncio.sleep(self.interval)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self.worker())
            logger.info(f"Solve queue worker started with interval {self.interval} seconds")

    async def stop(self):
        if self.is_running:
            self.is_running = False
            if self.task:
                await self.task
            self.task = None
            logger.info("Solve queue worker stopped")

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
            logger.info("Solve queue worker paused")

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            logger.info("Solve queue worker resumed")

    def reconfigure(self, new_interval: float):
        self.interval = new_interval
        logger.info(f"Solve queue worker reconfigured with new interval: {new_interval} seconds")

solve_queue_worker = SolveQueueWorker()

def get_solve_queue_worker() -> SolveQueueWorker:
    return solve_queue_worker
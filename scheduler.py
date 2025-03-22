import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the scheduler
scheduler = BackgroundScheduler()

def initialize_scheduler(update_function, interval_minutes=60):
    """
    Initialize the background scheduler to periodically update product data
    
    Args:
        update_function: The function to call when updating products
        interval_minutes: How often to run the update (in minutes)
    """
    try:
        # Add the job to the scheduler
        scheduler.add_job(
            func=update_function,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='update_products_job',
            name='Update product prices periodically',
            replace_existing=True
        )
        
        # Start the scheduler if it's not already running
        if not scheduler.running:
            scheduler.start()
            logger.info(f"Scheduler started. Will update products every {interval_minutes} minutes")
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")

def shutdown_scheduler():
    """
    Shutdown the scheduler when the application is stopping
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")

# For testing
if __name__ == "__main__":
    def test_update():
        logger.info("Test update running")
    
    initialize_scheduler(test_update, interval_minutes=1)
    
    # Keep the script running for testing
    import time
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        shutdown_scheduler()

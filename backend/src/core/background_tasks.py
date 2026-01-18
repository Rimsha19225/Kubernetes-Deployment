import asyncio
import logging
from datetime import timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..database.session import get_session
from ..utils.activity_logger import cleanup_old_activities

logger = logging.getLogger(__name__)

def start_background_cleanup():
    """Start background scheduler for cleanup tasks"""
    try:
        scheduler = AsyncIOScheduler()

        # Schedule cleanup to run every hour
        scheduler.add_job(
            func=perform_cleanup,
            trigger=IntervalTrigger(hours=1),
            id='activity_cleanup_job',
            name='Cleanup old activity logs',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Background cleanup scheduler started")

        # Shut down the scheduler when exiting the app
        import atexit
        atexit.register(lambda: scheduler.shutdown())

        return scheduler
    except ImportError:
        logger.warning("APScheduler not installed. Background cleanup will not be available.")
        return None


async def perform_cleanup():
    """Perform the actual cleanup operation"""
    try:
        db = next(get_session())
        deleted_count = cleanup_old_activities(db, hours_old=24)
        logger.info(f"Background cleanup completed. Deleted {deleted_count} old activity logs.")
    except Exception as e:
        logger.error(f"Error during background cleanup: {str(e)}")
    finally:
        try:
            db.close()
        except:
            pass
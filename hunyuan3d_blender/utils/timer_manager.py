import bpy
from typing import Dict, Callable, Optional

# Dictionary to store active timer callbacks: {uid: callback}
_active_timers: Dict[str, Callable] = {}

class TimerManager:
    """Manages Blender application timers (bpy.app.timers) with unique IDs."""

    @staticmethod
    def add(uid: str, callback: Callable, first_interval: float = 1.0):
        """Registers a timer callback if one with the same UID doesn't exist.

        Args:
            uid (str): A unique identifier for this timer.
            callback (Callable): The function to call periodically.
            first_interval (float): The interval in seconds between calls.
        """
        if TimerManager.exists(uid):
            print(f"Timer with UID '{uid}' already exists. Not adding.")
            return

        try:
            # persistent=False is important for timers managed this way,
            # otherwise they might persist across script reloads unexpectedly.
            bpy.app.timers.register(callback, first_interval=first_interval, persistent=False)
            _active_timers[uid] = callback
            print(f"Added timer '{uid}' with first interval {first_interval:.3f}s.")
        except Exception as e:
            print(f"Error registering timer '{uid}': {e}")

    @staticmethod
    def remove(uid: str):
        """Unregisters a timer callback identified by its UID."""
        if uid in _active_timers:
            callback = _active_timers.pop(uid)
            try:
                # Check if it's still registered before trying to unregister
                if bpy.app.timers.is_registered(callback):
                    bpy.app.timers.unregister(callback)
                    print(f"Removed timer '{uid}'.")
                # else:
                    # Timer might have stopped or been unregistered elsewhere
                    # print(f"Timer '{uid}' was already unregistered.") # Less verbose
            except Exception as e:
                print(f"Error unregistering timer '{uid}': {e}")
                # Ensure it's removed from tracking if it was present
                if uid in _active_timers: del _active_timers[uid] # Should be redundant due to pop
        # else: # Don't print if not found, remove() might be called defensively
            # print(f"Timer with UID '{uid}' not found for removal.")
            pass

    @staticmethod
    def exists(uid: str) -> bool:
        """Checks if a timer with the given UID is currently managed AND registered."""
        if uid in _active_timers:
            callback = _active_timers[uid]
            if bpy.app.timers.is_registered(callback):
                return True
            else:
                # Clean up stale entry from our manager if Blender says it's not registered
                print(f"Timer '{uid}' found in manager but not registered in Blender. Cleaning up.")
                del _active_timers[uid]
                return False
        return False

# --- Module Level Unregistration ---

def unregister():
    """Unregisters all active timers managed by this utility."""
    print("Unregistering all timers from TimerManager...")
    uids_to_remove = list(_active_timers.keys())
    for uid in uids_to_remove:
        TimerManager.remove(uid)
    print(f"Finished unregistering {len(uids_to_remove)} timers.")
    _active_timers.clear()

# This function should be called from the addon's main unregister function 
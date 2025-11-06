import json
import shutil
from pathlib import Path

class ChoreScheduler:
    def __init__(self, file_path="chores.json"):
        self.file = Path(file_path)
        self.data = self.load_data()

    # ---------- Basic File I/O ----------
    def load_data(self):
        if not self.file.exists():                
            sample_path = self.file.with_name("chores.json.sample")
            shutil.copy(sample_path, self.file)
            print(f"Created {self.file} from {sample_path}.")
        with self.file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self):
        with self.file.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # ---------- CRUD Operations ----------
    def get_assignments(self):
        return self.data["assignments"]

    def get_user_chore(self, user):
        return self.data["assignments"].get(user)

    def add_chore(self, chore):
        # Check if the chore exists
        if chore[0] in self.data["chores"].keys():
            raise ValueError("Chore already exists.")
        # Append the chore to the data
        self.data["chores"][chore[0]] = chore[1:]
        self.save_data()
    
    def remove_chore(self, chore):
        # Check if the chore exists
        if chore not in self.data["chores"].keys():
            raise ValueError(f'{chore} not in data')
        # Remove chore from the data
        self.data["chores"].pop(chore)
        self.save_data()

    def mark_completed(self, user):
        """Mark a user's chore as completed."""
        if user not in self.data["users"]:
            raise ValueError(f"User '{user}' not found.")
        if user not in self.data["completed"]:
            self.data["completed"].append(user)
            self.save_data()
            return True
        return False

    def reset_week(self):
        """Rotate chores and reset completion."""
        users = self.data["users"]
        chores = list(self.data["chores"].keys())
        assignments = self.data["assignments"]

        # Rotate chores
        current = [assignments[u] for u in users]
        rotated = current[-1:] + current[:-1]  # move last to first

        for u, c in zip(users, rotated):
            assignments[u] = c

        self.data["completed"] = []
        self.data["week"] += 1
        self.save_data()
        
    def add_user(self, user):
        if user in self.data["users"]:
            #raise ValueError("User already exists.")
            return
        self.data["users"].append(user)
        self.save_data()

    def remove_user(self, user):
        self.data["users"].remove(user)
        self.data["assignments"].pop(user, None)
        if user in self.data["completed"]:
            self.data["completed"].remove(user)
        self.save_data()

    #def set_rotation(self):
    # Raise an error if the chore count != users count
    # Take the weeks value, iterate through all the users
    # For each user, give them a chore offset and modulated by the weeks value
    # Apply that rotation

# Original code from fork
# Possibly unnecessary but keeping for posterity
'''
from typing import List, Text, Tuple

import calendar
import datetime
import discord
import logging
import pytablewriter

import util


class Scheduler:
  def __init__(self, users: List[discord.Member], logger_name='discord'):
    """Create a new scheduler.

    Args:
      users (List[discord.Member]): The users to put in the system.
      logger_name (str, optional): Logger's name. Defaults to 'discord'.
    """
    self.signed_off = False
    self._users = users
    self._logger = logging.getLogger(logger_name)

  @property
  def on_call(self) -> discord.Member:
    """Returns:
      discord.Member: Which discord user is on call for the chores tonight
    """
    return self._users[0]

  def generate_schedule(self) -> Text:
    """Generate a markdown representation of who is on call when.

    Returns:
      Text: User forcast for next 7 days, in a markdown table.
    """
    dow = datetime.datetime.today().weekday()

    if not self.signed_off:
      days = ['{} (today)'.format(calendar.day_abbr[dow])]
    else:
      days = ['{} (tmrw)'.format(calendar.day_abbr[dow + 1])]
    people = [util.discord_name(self._users[0])]

    for i in range(1, 7):
      if not self.signed_off:
        day_name = calendar.day_abbr[(dow + i) % 7]
      else:
        day_name = calendar.day_abbr[(dow + i + 1) % 7]
      days.append(day_name)

      user = self._users[i % len(self._users)]
      people.append(user.nick or user.name)

    writer = pytablewriter.MarkdownTableWriter(
      headers=days, value_matrix=[people])

    return writer.dumps()

  def swap(self, mem1: discord.Member, mem2: discord.Member):
    """Swap two user's positions in the queue.

    Args:
      mem1 (discord.Member): First member to swap
      mem2 (discord.Member): Second member to swap

    Raises:
      ValueError: Members are the same.
    """
    if mem1 == mem2:
      raise ValueError('Members need to be different.')

    mem1_idx = self._users.index(mem1)
    mem2_idx = self._users.index(mem2)

    self._users[mem1_idx] = mem2
    self._users[mem2_idx] = mem1

    self._logger.info('{} (id: {}) and {} (id: {}) have been swapped.'.format(
      util.discord_name(mem1), mem1.id, util.discord_name(mem2), mem2.id))
    self._logger.info('The user queue is now: [{}]'.format(
      ', '.join(util.discord_name(u) for u in self._users)))

  def signoff(self):
    """Signoff a user for completing their task."""
    self._users.append(self._users.pop(0))
    self.signed_off = True

    self._logger.info('{} (id: {}) has been signed off.'.format(
      util.discord_name(self._users[-1]), self._users[-1].id))
    self._logger.info('{} (id: {}) is now on call'.format(
      util.discord_name(self.on_call), self.on_call.id))
'''
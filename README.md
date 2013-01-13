BotCache is currently an alpha site - we're building a living archive of Twitter bots. You can see our progress at http://www.botcache.com.

---

Technical Steps for Confirming a Bot
Once you've confirmed a bot, you'll need to manually update its status in Terminal.  As so:

1. In Terminal:
import shelve
newshelf = shelve.open('botcachedb2',writeback=True)
newshelf['@bothandle'].status = 'confirmed
newshelf.close()

2. Then:
Run individbotdata.py to update its stats.

---

GNU Affero Public License Statement

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
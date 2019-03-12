import sys
from datetime import datetime, timedelta
from math import ceil
import time
from queue import Queue
# from collections import deque

import os
if os.name == 'nt':
	import ctypes
	kernel32 = ctypes.windll.kernel32
	kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class ProgressBar:

	# Clear line: \033[K
	# Go up one line: \033[F
	
	def __init__(self, total = None, name = "", parent = None, barType = "=", capacity = 20, previousDuration = timedelta(seconds=0)):
		
		self.startTime = datetime.now();		
		self.capacity = capacity;
		self.parent = parent;
		self.isRoot = True if parent is None else False;
		self.barType = barType if parent is None else "-";
		
		self.name = name;
		self.total = total;
		self.processed = 0;
		self.elapsed = timedelta(seconds=0) + previousDuration;
		self.previousDuration = previousDuration;
		
		self.rateAnalysisWindowSize = 6;
		self.timePtHistory = Queue(self.rateAnalysisWindowSize);
		for i in range(self.rateAnalysisWindowSize - 1):
			self.timePtHistory.put(datetime.now());
		
		#Print progress bar and percentage
		sys.stdout.write("\n"); #make room for progress bar
		print("{:20} [{:<{}}] \033[1;32m{:.1f}%\033[0m".format(
			self.name, self.barType * 0, self.capacity, 0
		), end="", flush=True);
		
	def displayProgress(self, processed, printTimeStats = True, printIterationRate = True):
	
		#If parent exists update parent with respect to child
		if self.isRoot == False:			
			sys.stdout.write("\033[F"); #move cursor up one level to parent progress bar
			parentProcessed = self.parent.processed + (1 / self.total);
			self.parent.displayProgress(parentProcessed);
			sys.stdout.write("\n"); #return cursor to child progress bar
	
		if len(self.name) > 43:
			self.name = self.name[:40] + "...";
		
		self.processed = processed;
		self.elapsed = datetime.now() - self.startTime + self.previousDuration;
		
		self.timePtHistory.put(datetime.now());
		rateAnalysisWindow = datetime.now() - self.timePtHistory.get();
		iterationRate = (rateAnalysisWindow.microseconds / 1000000 + rateAnalysisWindow.seconds) / (self.rateAnalysisWindowSize - 1);
		
		#Only create progress bar and time remaining if total exists which is mandatory for calcualtions
		if isinstance(self.total, (int, float)):
			
			#Progress Stats
			numBars = ceil(processed / self.total * self.capacity);
			progress = float(processed / self.total * 100) if processed > 0 else 1; #Progress measured as %
			remaining = max((100 - progress) * (self.elapsed / progress), timedelta(seconds=0));
		
			#Print progress bar and percentage
			sys.stdout.write("\033[K\r"); #Clear line and move cursor to front of line
			print("{: <43} [{:<{}}] \033[1;32m{:6.1f}%\033[0m".format(
				self.name, self.barType * numBars, self.capacity, progress
				), end=""
			);
			
			#Print elapsed/remaining time
			if printTimeStats == True:			
				print("  Elapsed: {} Remaining: {}".format(
					self.timeDeltaFormatter(self.elapsed), self.timeDeltaFormatter(remaining), iterationRate
				), end="");
		else:
			#Print progress bar and number iterated
			sys.stdout.write("\033[K\033[K\r"); #Clear line and move cursor to front of line
			print("{: <43} | Processed: \033[1;32m{}\033[0m | Elapsed: {}".format(self.name, self.processed, self.timeDeltaFormatter(self.elapsed)), end="");
		
		#Print iterations/sec
		if printIterationRate == True:
			print(" @ {:.1f} iters/sec".format(
				iterationRate
			), end="");
		
		#move cursor back to root when child finished
		if self.processed == self.total and self.isRoot == False:
			sys.stdout.write("\033[F"); 
		
		self.clearTerminal();
		sys.stdout.flush(); #flush output buffer to terminal
		
	def timeDeltaFormatter(self, td_object):
		
		totalSeconds = td_object.total_seconds();
		days, hours = divmod(totalSeconds, 86400);
		hours, minutes = divmod(hours, 3600);
		minutes, seconds = divmod(minutes, 60);
		
		duration = "";
		if days != 0:
			duration += str(int(days)) + (" days " if days > 1 else " day ");
		if hours != 0:
			duration += str(int(hours)) + (" hours " if hours > 1 else " hour ");
		if minutes != 0:
			duration += str(int(minutes)) + ("mins " if minutes > 1 else "min ");
		if seconds != 0:
			duration += str(int(seconds)) + ("secs " if seconds > 1 else "s ");
		else:
			duration = "0s";
			
		return duration;
	
	def clearTerminal(self, lines = 7):
		for i in range(lines):
			sys.stdout.write("\n\033[K"); #clear line
		for i in range(lines):	
			sys.stdout.write("\033[F"); #clear line
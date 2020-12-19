from enum import Enum
class LogLevel(Enum):
	EMERGENCY = 0
	ALERT = 1
	CRITICAL = 2
	ERROR = 3
	WARNING = 4
	NOTICE = 5
	INFO = 6
	DEBUG = 7
	VERBOSE = 8
	def __ge__(self, other):
		return self.value >= other.value
class Logger():
	LOG_LEVEL=LogLevel.INFO
	@staticmethod
	def log(msg, args=[], msgLogLevel=LogLevel.INFO, logEachLine=True):
		#Todo: we don't want the surrounding parenthesis around each argument.  Need to refactor how we're stripping this.  Is there a more efficient way to do this?
		#Consider allowing for all separate lines to be prefixed withe the DATETIME and msglevel.
		from datetime import datetime
		if Logger.LOG_LEVEL >= msgLogLevel:
			if logEachLine:
				msg=msg.replace("\n", "\n"+f"{datetime.now()}, {msgLogLevel.name}({msgLogLevel.value}), ")
			myStr = ", " + msg
			if len(args)>=1:
				myStr += ", ARGS:"
			for a in args:
				a=str(a).lstrip('(').rstrip(')')
				myStr += ", " + a
			print(f"{datetime.now()}, {msgLogLevel.name}({msgLogLevel.value}){myStr}")

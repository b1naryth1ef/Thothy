#Thothy

Another attempt at a distributed, fast, and smart irc bot.

#Implementation Notes/Spec sheet
To remain distributed, Thothy is split into two main parts, SLAVES and MASTERS. The masters shouldnt connect to irc, and the SLAVES should never parse any information, simply read and write.


# WhatsAppAnalytics

This is an unfinished project for WhatsApp message analytics which I try to develop in my limited free time. Feel free to hop in, commits are welcomed. 

Currently it reads from WhatsApp export of chat (it should be exported without media). Creates a df and tries to find conversations (a message sequence with messages apart of eachother max 300 seconds). Lastly it calculates sentiment score for each message. Later on these findings can be used to calculate total sentiment for each conversation. (haven't implemented that part yet)

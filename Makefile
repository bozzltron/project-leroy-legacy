sync-from:
	rsync -aP pi@10.0.4.79:~/Projects/project-birdfeeder/ ~/Projects/personal/project-everette 

sync-to:
	rsync -aP ~/Projects/personal/project-everette/ pi@10.0.4.79:~/Projects/project-birdfeeder
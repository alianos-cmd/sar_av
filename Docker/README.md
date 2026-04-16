Für unserer Projekt nutzen wir Docker
Dafür benötigt ihr vorab: Docker, Docker Compose

	> curl -sSL https://get.docker.com
	> apt install docker-compose
	> sh sudo usermod -aG docker $USER

1. Kopiert euch dann bitte diesen Ordner auf euer Gerät. 
2. Auf eurem Gerät in der Kommandozeile: Navigiert ihr bitte zu dem neuen Ordner. Auf Unix Systemen funtioniert das mit "cd". 
3. In dem Ordner angekommen führt ihr nun den Befehl aus: 

	> docker-compose up --build

	Es kann passieren, dass ihr dann erstmal beim Mounten der Bash ihr bei "Attaching to ros2_robot" hängen bleibt. 
	Dann einfach mit "control+C" schließen. 

4. Bei nächsten Mal den Container einfach mit 

	> docker-compose run ros2 

	starten. 

	Ihr müsstet nun in der bash des containers landen.

5. Bitte einmal testen, ob der persistent Speicher funktioniert: 

	Dafür erstellt ihr im Container im Ordner "ros_ws" eine text datei. 

	> cd /ros_ws
	> touch test.txt

	schließt den Container mit

	> exit

	Nun sollte die Datei auf dem Host zu finden sein.

6. Ihr solltet nun Zugang zu der Hardware über den dev Ordner haben.  


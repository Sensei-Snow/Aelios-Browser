<div align="center">
    <img src="assets/logo_title.png" alt="Aelios Logo" width="400"/>
</div>

<h3>Here is the code for Aelios Browser, a simple, privacy-friendly Chromium browser coded with Python and the PyQt5 library.</h3>
<br>

<div align="center">
    <img src="assets/aelios.png" alt="Aelios Screenshot" width="700"/>
</div>
<br>

<hr style="height:2px; background-color:gray; border:none;">
<br>

<h4>First stage :</h4>
To access to the Tor network, you'll need to download the executable. With this little application, the programm will have the possibility to switch between the Tor network and the regular internet.
<br><br>
Here is the link if you want to download the Tor executable : https://www.torproject.org/download/tor/
<br><br>
Then, you'll need to write the path to your own Tor executable in <code>config.json</code> :

```json
{
    "tor_path": "path\\to\\your\\tor\\executable",
    "comment": "Change the tor_path with your own path which goes to the Tor executable, see the README.md for more informations"
}
```
<br>

<hr style="height:2px; background-color:gray; border:none;">
<br>

<h4>Second stage :</h4>

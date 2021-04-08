from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<a href="/" onclick="sound()">NORMAL LINK</a><br>

<a href="javascript:void(0);" onclick="sound('{{item}}')">JAVASCRIPT LINK</a>

<script>
function sound(item) {
    //alert("SOUND");
    var audio = new Audio('/static/letitgo.mp3');
    // reload after audio
    audio.onended = function() { window.location.href="/delete/" + item; }
    audio.play();
}
</script>
''', item="somevalue")

app.run()

//あたらしいやつ
chunks = [];
const buttonStart = document.querySelector('#buttonStart')
const buttonStop = document.querySelector('#buttonStop')
const buttonSend = document.querySelector('#buttonSend')
const player = document.querySelector('#player')
const openconsole = document.querySelector('#console')
const isDebugSwitch = document.getElementById('debugbutton')
var isDebugMode = 0;
voiceURL = null
//postURL = 'https://hoge.fuga/upload'
// postURL = 'http://127.0.0.1:8000/upload/testfile'
postURL = 'http://sssuma.com/upload/testfile'

window.onload = () => {
    openconsole.insertAdjacentHTML('beforeend', '[MESSAGE] Loading...<br>')
    openconsoleScroll()

    if (!navigator.mediaDevices) {
        console.log("Media Devices not supported!!");
        openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> Media devices not supported.<br>')
        openconsoleScroll()
        return;
    }

    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        readyMediaRecorder(stream); // Ready for Rec.
        openconsole.insertAdjacentHTML('beforeend', '<font color="#3d2">[SUCCESS]</font> Ready for Recording.<br>')
        openconsoleScroll()
    }).catch((err) => {
        console.log("Error:" + err); // Error
        openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> Any media devices are none.<br>')
        openconsoleScroll()
    });
}

function readyMediaRecorder(stream) {

    let mediaRecorder = new MediaRecorder(stream)

    mediaRecorder.onstop = (e) => {
        openconsole.insertAdjacentHTML('beforeend', '[MESSAGE] Stop recording<br>')
        openconsoleScroll()
        const blob = new Blob(chunks, { "type": "audio/ogg; codecs=opus" }) //save as OGG. i hate mp3
        voiceURL = blob
        //console.log("停止時のblob URL" + voiceURL)
        chunks = [] // initing

        player.src = URL.createObjectURL(blob) // player(for soundplay)
        buttonSend.removeAttribute('disabled')

        reader = new FileReader() // fileReader(for POST)
        reader.readAsDataURL(blob)
    }

    mediaRecorder.ondataavailable = (e) => {
        chunks.push(e.data)
    }

    mediaRecorder.onerror = (e) => {
        console.log("MediaRecorder onerror:" + e)
        openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> MediaRecorder onerror: ' + e + '<br>')
        openconsoleScroll()
    }

    buttonStart.onclick = () => {
        if (mediaRecorder.state == "recording") return
        mediaRecorder.start()
        buttonStart.setAttribute('disabled', '')
        buttonStop.removeAttribute('disabled')
        openconsole.insertAdjacentHTML('beforeend', '[MESSAGE] Start recording<br>')
        openconsoleScroll()
    }

    buttonStop.onclick = () => {
        if (mediaRecorder.state == "inactive") return
        mediaRecorder.stop()
        buttonStop.setAttribute('disabled', '')
        buttonStart.removeAttribute('disabled')
    }

    buttonSend.onclick = async () => {
        if (mediaRecorder.state == "recording") return

        try {
            // POST
            var statuscode = await sendAudio(voiceURL);
            console.log('statuscode: ' + statuscode);

            // 200だかなんだかが返ってきたら進む
            if (statuscode == 200) {
                URL.revokeObjectURL(player.src);
                buttonSend.setAttribute('disabled', '');
                openconsole.insertAdjacentHTML('beforeend', '[MESSAGE] Cleanup was done.<br>')
                openconsoleScroll()
            } else {
                console.error('エラーが発生しました:', error);
                openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> Error(s) exist.<br>')
                openconsoleScroll()
            }
        } catch (error) {
            console.error('エラーが発生しました:', error);
            openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> Error(s) exist.<br>')
            openconsoleScroll()
        }
    }
}

async function sendAudio(targetblob) {
    var sending = new FormData()
    sending.append('audio', targetblob)

    try {
        const response = await fetch(postURL, {
            method: 'POST',
            body: sending
        });

        openconsole.insertAdjacentHTML('beforeend', '<font color="#3d2">[SUCCESS]</font> HTTP statuscode:' + response.status + '<br>')
        openconsoleScroll()
        console.log('そうしんしたよ statuscodeは' + response.status + 'だよ');
        return response.status;
    } catch (error) {
        console.error('えらーだよ ないようは' + error + 'だよ');
        openconsole.insertAdjacentHTML('beforeend', '<font color="#e11">[ERROR]</font> Error(s) exist:' + error + '<br>')
        openconsoleScroll()
        throw error;
    }
}

isDebugSwitch.onclick = () => {
    if (isDebugMode) {
        openconsole.style.maxWidth = '0px'
        isDebugMode = 0
    } else {
        openconsole.style.maxWidth = ''
        isDebugMode = 1
    }
}


function openconsoleScroll() {
    openconsole,
        areaHeight = openconsole.scrollHeight;
    openconsole.scrollTop = areaHeight;
}
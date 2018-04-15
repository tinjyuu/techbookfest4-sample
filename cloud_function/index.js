'use strict';
 
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion} = require('dialogflow-fulfillment');
 
process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
// init firebase
const admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);
var db = admin.firestore();

exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));
  const parameters = request.body.result.parameters;

  function welcome(agent) {
    agent.add(`ようこそ`);
  }
 
  function fallback(agent) {
    agent.add(`ヘルシェイク矢野ことを考えていて聞いていませんでした`);
    agent.add(`もう一度お願いします`);
}

function start(agent) {
  var docRef = db.collection('robots').doc('orekame');

  var setAda = docRef.set({
      status: "run",
  });
  agent.add(`デストロイヤーの起動をします...`);
}

function end(agent) {
  var docRef = db.collection('robots').doc('orekame');

  var setAda = docRef.set({
      status: "stop",
  });
  agent.add(`デストロイヤーを終了をします...`);
}

function command(agent) {
    var docRef = db.collection('robots').doc('orekame');

    var setAda = docRef.set({
        command: parameters.command,
    });
    agent.add(`${parameters.command} を実行します`);
}
// Run the proper function handler based on the matched Dialogflow intent name
let intentMap = new Map();
intentMap.set('Default Welcome Intent', welcome);
intentMap.set('Default Fallback Intent', fallback);
intentMap.set('command', command);
intentMap.set('start', start);
intentMap.set('end', end);
agent.handleRequest(intentMap);
});

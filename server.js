const Discord = require("discord.js");
const { api, prefix, token, master } = require("./config.json");
const { good_taste_messages, bad_taste_messages } = require("./constants.json");

const https = require('https');
const ytdl = require("ytdl-core");
const client = new Discord.Client();
const queue = new Map();

client.once("ready", () => {
  console.log("Ready!");
});

client.once("reconnecting", () => {
  console.log("Reconnecting!");
});

client.once("disconnect", () => {
  console.log("Disconnect!");
});

client.on("message", async message => {
  if (message.author.bot) return;
  if (!message.content.startsWith(prefix)) return;

  const serverQueue = queue.get(message.guild.id);
  let args = message.content.slice(prefix.length).split(' ');
  let random_number = await randomize_number(5);
  if(args[0] === "insult") await insult(message, args[1])
  
  else if (message.content.startsWith(`${prefix}add`) || message.content.startsWith(`${prefix}play`)) {
    if(message.author.id == master)  message.channel.send(good_taste_messages[random_number]);
    else message.channel.send(bad_taste_messages[random_number]);
    
    if (message.content.startsWith(`${prefix}play`)) await add_in_playlist(message, serverQueue, "add");
    if (message.content.startsWith(`${prefix}play-rn`)) await add_in_playlist(message, serverQueue, "play");
  }
  
  else if (message.content.startsWith(`${prefix}skip`)) await skip(message, serverQueue);
  else if (message.content.startsWith(`${prefix}stop`)) stop(message, serverQueue);
  else message.channel.send("You need to enter a valid command!");
  
});
// --------------------------- OFENSIVE BUDDY -----------------------------------------

async function insult(message, victim){
  https.get(api, (resp) => {
  let data = '';

  // A chunk of data has been recieved.
  resp.on('data', (chunk) => {
    data += chunk;
  });

  // The whole response has been received. Print out the result.
  resp.on('end', () => {
    console.log(JSON.parse(data).insult);
    let response = JSON.parse(data).insult;
    if(message.author.id == master) message.channel.send(victim + " " + response);
    else message.channel.send("Fuck you, <@" + message.author.id + ">");
  });

  }).on("error", (err) => {
    if(message.author.id == master) message.channel.send("Fuck you, " + victim);
    else message.channel.send("Fuck you, <@" + message.author.id + ">");
  });

  
}

// --------------------------- MUSIC PLAYER --------------------------------------------

async function randomize_number(max) {
  return Math.floor(Math.random() * Math.floor(max));
}

async function add_in_playlist(message, serverQueue, command) {
  let args = message.content.split(" ");

  const voiceChannel = message.member.voice.channel;
  if (!voiceChannel)
    return message.channel.send(
      "You need to be in a voice channel to play music!"
    );
  const permissions = voiceChannel.permissionsFor(message.client.user);
  if (!permissions.has("CONNECT") || !permissions.has("SPEAK")) {
    return message.channel.send(
      "I need the permissions to join and speak in your voice channel!"
    );
  }
  console.log("Playing: " + args[1]);
  const songInfo = await ytdl.getInfo(args[1]); //with cmnd node has to be index 2, npm start 1. dunno y, maybe the node versions diferent
  const song = {
    title: songInfo.title,
    url: songInfo.video_url
  };

  if (!serverQueue || command == "play") {
    const queueContruct = {
      textChannel: message.channel,
      voiceChannel: voiceChannel,
      connection: null,
      songs: [],
      volume: 5,
      playing: true
    };

    queue.set(message.guild.id, queueContruct);

    queueContruct.songs.push(song);

    try {
      var connection = await voiceChannel.join();
      queueContruct.connection = connection;
      play(message.guild, queueContruct.songs[0]);
    } catch (err) {
      console.log(err);
      queue.delete(message.guild.id);
      return message.channel.send(err);
    }
  } else {
    serverQueue.songs.push(song);
    return message.channel.send(`${song.title} has been added to the queue!`);
  }
}

async function skip(message, serverQueue) {
  if (!message.member.voice.channel)
    return message.channel.send(
      "You have to be in a voice channel to stop the music!"
    );
  if (!serverQueue)
    return message.channel.send("There is no song that I could skip!");
  serverQueue.connection.dispatcher.end();
}

function stop(message, serverQueue) {
  if (!message.member.voice.channel)
    return message.channel.send(
      "You have to be in a voice channel to stop the music!"
    );
  serverQueue.songs = [];
  serverQueue.connection.dispatcher.end();
}

function play(guild, song) {
  const serverQueue = queue.get(guild.id);
  if (!song) {
    serverQueue.voiceChannel.leave();
    queue.delete(guild.id);
    return;
  }

  const dispatcher = serverQueue.connection
    .play(ytdl(song.url))
    .on("finish", () => {
      serverQueue.songs.shift();
      play(guild, serverQueue.songs[0]);
    })
    .on("error", error => console.error(error));
  dispatcher.setVolumeLogarithmic(serverQueue.volume / 5);
  serverQueue.textChannel.send(`Start playing: **${song.title}**`);
}

client.login(token);
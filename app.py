#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from bottle import get, run, static_file, template, redirect
from py2neo import Graph
from bs4 import BeautifulSoup, NavigableString
from soupselect import select

graph = Graph()

@get('/css/<filename:re:.*\.css>')
def get_css(filename):
    return static_file(filename, root="static", mimetype="text/css")


@get('/images/<filename:re:.*\.png>')
def get_image(filename):
    return static_file(filename, root="static", mimetype="image/png")

@get("/")
def get_index():
     redirect("/episodes")

@get("/episodes")
def get_episodes():
    """ List of all episodes.
    """
    statement = """\
    MATCH (e:Episode)
    RETURN e.id AS id, e.title as title, e.number as number, e.season as season
    ORDER BY id
    """
    return template("episodes", episodes=graph.cypher.execute(statement))

@get("/episodes/<episode_id>")
def get_episode(episode_id):
    """ Show specific episode
    """
    statement = """\
    MATCH (e:Episode {id: {episodeId}})-[r:TOPIC]->(topic)
    WITH e, r, topic ORDER BY r.score DESC
    RETURN e.id AS id, e.title as title, e.season AS season, e.number AS number,
           COLLECT({id: topic.id, name: topic.value, score: r.score}) AS topics
    ORDER BY id
    """

    episode = graph.cypher.execute(statement, {"episodeId": int(episode_id)})[0]

    season = episode["season"]
    number = episode["number"]

    transcript = open("data/transcripts/S%d-Ep%d" %(season, number)).read()
    soup = BeautifulSoup(transcript)
    rows = select(soup, "table.tablebg tr td.post-body div.postbody")

    return template("episode", episode = episode, transcript = rows[0])

@get("/topics/<topic_id>")
def get_topic(topic_id):
    """ Show specific topic
    """
    statement = """\
    MATCH (topic:Topic {id: {topicId}})<-[r:TOPIC]-(e)
    WITH e, r, topic ORDER BY r.score DESC
    RETURN topic.id AS id, topic.value as value,
           COLLECT({id: e.id, title: e.title, score: r.score}) AS episodes
    ORDER BY id
    """
    topic = graph.cypher.execute(statement, {"topicId": int(topic_id)})[0]

    return template("topic", topic = topic)

if __name__ == "__main__":
    run(host="localhost", port=8000, reloader=True, debug = True)
from flask import Flask, render_template, request, redirect, url_for 
import sqlite3

app = Flask(__name__)
DATABASE = 'gestao_clientes.db'

def conectar_db():
    return sqlite3.connect(DATABASE)


def get_db_connection():
    conn = sqlite3.connect("gestao_clientes.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

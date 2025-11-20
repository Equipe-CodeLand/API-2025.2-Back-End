import { Request, Response } from "express";
import axios from "axios";
import db from "../db/db";

const PLN_URL = "http://127.0.0.1:5000";

async function enviarMensagem(req: Request, res: Response) {
    try{
        const usuarioId = req.user?.id;
        const chatId = req.body.chat_id;
        const texto = req.body.texto;
        const data = new Date();

        await db.query(
          "INSERT INTO chat_mensagens (chat_id, usuario_id, mensagem, tipo, criado_em) VALUES (?, ?, ?, ?, ?)",
          [chatId, usuarioId, texto, "usuario", data]
        );

        const resp = await axios.post(`${PLN_URL}/chat`, {
          usuario_id: usuarioId,
          texto: req.body.texto
        });

        const respostaBot = resp.data.resposta;
        const dataBot = new Date();

        await db.query(
          "INSERT INTO chat_mensagens (chat_id, usuario_id, mensagem, tipo, criado_em) VALUES (?, ?, ?, ?, ?)",
          [chatId, null, respostaBot, "bot", dataBot]
        );

        return res.json(resp.data);
      } 
      catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao gerar relatório" + err.message });
      }
}

async function criarChat(req: Request, res: Response) {
    try {
        const usuarioId = req.user?.id;
        const primeiraMensagem = req.body.primeira_mensagem;
        const data = new Date();

        const [chatResult]: any = await db.query(
            "INSERT INTO chat (titulo, criado_em) VALUES (?, ?)",
            [primeiraMensagem, data]
        );

        const chatId = chatResult.insertId; 

        await db.query(
            "INSERT INTO chat_usuario (chat_id, usuario_id) VALUES (?, ?)",
            [chatId, usuarioId]
        );

        await db.query(
            "INSERT INTO chat_mensagens (chat_id, usuario_id, mensagem, tipo, criado_em) VALUES (?, ?, ?, ?, ?)",
            [chatId, usuarioId, primeiraMensagem, "usuario", data]
        );

        return res.json({
            chat_id: chatId,
            primeira_mensagem: primeiraMensagem
        });

    } catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao criar chat: " + err.message });
    }
}

export default {
    enviarMensagem,
    criarChat
};
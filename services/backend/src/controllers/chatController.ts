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


        return res.json({
            chat_id: chatId,
            primeira_mensagem: primeiraMensagem
        });

    } catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao criar chat: " + err.message });
    }
}



async function listarChats(req: Request, res: Response) {
    try {
        const usuarioId = req.user?.id;

        if (!usuarioId) {
            return res.status(401).json({ error: "Usuário não autenticado" });
        }

        // Buscar todos os chats do usuário
        const [chats]: any = await db.query(
            `
            SELECT 
                c.id AS chat_id,
                c.titulo,
                c.criado_em,
                (
                    SELECT mensagem 
                    FROM chat_mensagens 
                    WHERE chat_id = c.id 
                    ORDER BY criado_em DESC 
                    LIMIT 1
                ) AS ultima_mensagem,
                (
                    SELECT criado_em
                    FROM chat_mensagens 
                    WHERE chat_id = c.id 
                    ORDER BY criado_em DESC 
                    LIMIT 1
                ) AS ultima_interacao
            FROM chat c
            INNER JOIN chat_usuario cu ON cu.chat_id = c.id
            WHERE cu.usuario_id = ?
            ORDER BY ultima_interacao DESC
            `,
            [usuarioId]
        );

        return res.json({ chats });

    } catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao buscar chats: " + err.message });
    }
}

async function listarMensagens(req: Request, res: Response) {
    try {
        const usuarioId = req.user?.id;
        const chatId = req.params.chatId;

        if (!usuarioId) {
            return res.status(401).json({ error: "Usuário não autenticado" });
        }

        if (!chatId) {
            return res.status(400).json({ error: "Chat ID não informado" });
        }

        // Verifica se o usuário realmente participa deste chat
        const [verifica]: any = await db.query(
            "SELECT 1 FROM chat_usuario WHERE chat_id = ? AND usuario_id = ?",
            [chatId, usuarioId]
        );

        if (verifica.length === 0) {
            return res.status(403).json({ error: "Você não tem acesso a este chat" });
        }

        // Busca todas as mensagens do chat
        const [mensagens]: any = await db.query(
            `
            SELECT 
                id,
                chat_id,
                usuario_id,
                mensagem,
                tipo,
                criado_em
            FROM chat_mensagens
            WHERE chat_id = ?
            ORDER BY criado_em ASC
            `,
            [chatId]
        );

        return res.json({ chat_id: chatId, mensagens });

    } catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao buscar mensagens: " + err.message });
    }
}

export default {
    enviarMensagem,
    criarChat,
    listarChats,
    listarMensagens
};

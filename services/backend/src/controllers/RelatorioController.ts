import { Response } from "express";
import axios from "axios";
import { AuthRequest } from "../middlewares/auth";
import db from "../db/db";

const PLN_URL = "http://localhost:5000";

export async function gerarRelatorioGeral(req: AuthRequest, res: Response) {
  try {
    const usuarioId = req.user.id;
    const resp = await axios.post(`${PLN_URL}/relatorio`, {
      usuario_id: usuarioId,
    });

    return res.json(resp.data);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao gerar relatório" });
  }
}

export async function gerarRelatorioSku(req: AuthRequest, res: Response) {
  try {
    const usuarioId = req.user.id;
    const resp = await axios.post(`${PLN_URL}/relatorio-skus`, {
      usuario_id: usuarioId,
    });

    return res.json(resp.data);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao gerar relatório SKU" });
  }
}

export async function listarRelatorios(req: AuthRequest, res: Response) {
  try {
    const usuarioId = req.user.id;

    const [relatorios] = await db.query(
      `SELECT id, titulo, caminho_arquivo, criado_em 
       FROM relatorio 
       WHERE usuario_id = ? 
       ORDER BY criado_em DESC`,
      [usuarioId],
    );

    // lê o conteudo do relatório com base no arquivo salvo do backend.
    const relatoriosComConteudo = await Promise.all(
      relatorios.map(async (rel: any) => {
        try {
          const resp = await axios.get(`${PLN_URL}/relatorio/conteudo`, {
            params: { caminho: rel.caminho_arquivo },
          });
          return { ...rel, conteudo: resp.data.conteudo };
        } catch {
          return { ...rel, conteudo: "Arquivo não encontrado" };
        }
      }),
    );

    return res.json(relatoriosComConteudo);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao listar relatórios" });
  }
}

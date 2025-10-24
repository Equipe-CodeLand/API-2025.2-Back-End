import { Request, Response } from "express";
import axios from "axios";
import db from "../db/db";

const PLN_URL = "http://127.0.0.1:5000";

export async function gerarRelatorioGeral(req: Request, res: Response) {
  try {
    const usuarioId = req.user?.id;
    const resp = await axios.post(`${PLN_URL}/relatorio`, {
      usuario_id: usuarioId,
    });

    return res.json(resp.data);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao gerar relatório" });
  }
}

export async function gerarRelatorioSku(req: Request, res: Response) {
  try {
    const usuarioId = req.user?.id;
    const resp = await axios.post(`${PLN_URL}/relatorio-skus`, {
      usuario_id: usuarioId,
      data_inicio: req.body.data_inicio,
      data_fim: req.body.data_fim,
      incluir_todos_skus: req.body.incluir_todos_skus,
      skus: req.body.skus,
      topicos: req.body.topicos
    });

    return res.json(resp.data);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao gerar relatório SKU" });
  }
}

export async function listarRelatorios(req: Request, res: Response) {
  try {
    const usuarioId = req.user?.id;

    const [relatorios] = await db.query(
      `SELECT id, titulo, caminho_arquivo, criado_em 
       FROM relatorio 
       WHERE usuario_id = ? 
       ORDER BY criado_em DESC`,
      [usuarioId],
    );

    // lê o conteudo do relatório com base no arquivo salvo do backend.
    const relatoriosComConteudo = await Promise.all(
      (relatorios as any[]).map(async (rel: any) => {
        try {
          const resp = await axios.get(`${PLN_URL}/relatorio/conteudo`, {
            params: { caminho: rel.caminho_arquivo },
          });
          return { ...rel, conteudo: (resp.data as any).conteudo };
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

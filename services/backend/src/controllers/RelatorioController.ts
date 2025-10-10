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

export async function atualizarRelatorio(req: Request, res: Response) {
  const { id } = req.params;
  const { titulo } = req.body;

  if (!titulo || titulo.trim() === "") {
    return res.status(400).json({ error: "O título é obrigatório." });
  }

  try {
    const [rows] = await db.query("SELECT * FROM relatorio WHERE id = ?", [id]);
    if ((rows as any[]).length === 0) {
      return res.status(404).json({ error: "Relatório não encontrado." });
    }

    await db.execute("UPDATE relatorio SET titulo = ? WHERE id = ?", [
      titulo,
      id,
    ]);
    return res
      .status(200)
      .json({ message: "Relatório atualizado com sucesso." });
  } catch (err) {
    console.error("Erro ao atualizar relatório:", err);
    return res.status(500).json({ error: "Erro ao atualizar relatório." });
  }
}


export async function excluirRelatorio(req: Request, res: Response) {
  try {
    const usuarioId = req.user?.id;
    const relatorioId = req.params.id;
    
    const [rows]: any = await db.query(
      "SELECT caminho_arquivo FROM relatorio WHERE id = ? AND usuario_id = ?",
      [relatorioId, usuarioId],
    );

    if (!rows.length) {
      return res.status(404).json({ error: "Relatório não encontrado" });
    }

    const caminhoArquivo = rows[0].caminho_arquivo;

    await db.query("DELETE FROM relatorio WHERE id = ? AND usuario_id = ?", [
      relatorioId,
      usuarioId,
    ]);

    // notifica o microserviço PLN para apagar o arquivo
    try {
      await axios.delete(`${PLN_URL}/relatorio/remover`, {
        params: { caminho: caminhoArquivo },
      });
    } catch {
      console.warn("Aviso: não foi possível remover o arquivo do PLN.");
    }

    return res.json({ message: "Relatório excluído com sucesso" });
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao excluir relatório" });
  }
}

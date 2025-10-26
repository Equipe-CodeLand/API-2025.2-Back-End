import { Request, Response } from "express";
import axios from "axios";
import db from "../db/db";
import { enviarEmail } from "../services/emailService"; // ADICIONADO

const PLN_URL = "http://127.0.0.1:5000";

export async function gerarRelatorioGeral(req: Request, res: Response) {
  try {
    const usuarioId = req.user?.id;
    const resp = await axios.post(`${PLN_URL}/relatorio`, {
      usuario_id: usuarioId,
    });

    // retorna normalmente ao caller
    const retorno = resp.data;

    // Tenta enviar email se o usuário permitiu receber emails
    (async () => {
      try {
        if (req.user?.receberEmails) {
          const caminho = retorno.arquivo;
          // obter o conteúdo salvo (PLN)
          const conteudoResp = await axios.get(`${PLN_URL}/relatorio/conteudo`, { params: { caminho } });
          const conteudoFormatado = formatContentForEmail(conteudoResp.data?.conteudo ?? retorno.dados);
          const assunto = `Relatório Geral - ${new Date().toLocaleDateString("pt-BR")}`;
          const html = `<h3>Olá, ${req.user?.nome}</h3><p>Segue em anexo o Relatório Geral.</p><pre style="white-space:pre-wrap">${conteudoFormatado}</pre>`;
          await enviarEmail({
            to: req.user.email,
            subject: assunto,
            html,
            attachments: [{
              filename: `relatorio_geral_${new Date().toISOString().slice(0,10)}.txt`,
              content: conteudoFormatado
            }]
          });
          console.log("Email automático de Relatório Geral enviado para:", req.user.email);
        }
      } catch (e) {
        console.error("Falha no envio automático de email (Relatório Geral):", e);
      }
    })();

    return res.json(retorno);
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

    const retorno = resp.data;

    (async () => {
      try {
        if (req.user?.receberEmails) {
          const caminho = retorno.arquivo;
          const conteudoResp = await axios.get(`${PLN_URL}/relatorio/conteudo`, { params: { caminho } });
          // PLN pode devolver array (texto em parágrafos) ou já texto
          const conteudoFormatado = formatContentForEmail(conteudoResp.data?.conteudo ?? retorno.conteudo);
          const assunto = `Relatório por SKU - ${new Date().toLocaleDateString("pt-BR")}`;
          const html = `<h3>Olá, ${req.user?.nome}</h3><p>Segue em anexo o Relatório por SKU.</p><pre style="white-space:pre-wrap">${conteudoFormatado}</pre>`;
          await enviarEmail({
            to: req.user.email,
            subject: assunto,
            html,
            attachments: [{
              filename: `relatorio_sku_${new Date().toISOString().slice(0,10)}.txt`,
              content: conteudoFormatado
            }]
          });
          console.log("Email automático de Relatório por SKU enviado para:", req.user.email);
        }
      } catch (e) {
        console.error("Falha no envio automático de email (Relatório SKU):", e);
      }
    })();

    return res.json(retorno);
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro ao gerar relatório SKU" });
  }
}

// Função utilitária local para garantir que o conteúdo seja texto simples
function formatContentForEmail(conteudo: any): string {
  if (!conteudo) return "Conteúdo não disponível";
  if (Array.isArray(conteudo)) return conteudo.join("\n\n");
  if (typeof conteudo === "object") {
    return Object.entries(conteudo)
      .map(([k, v]) => {
        if (Array.isArray(v)) return `${k}: ${v.length ? v.join(", ") : "Nenhum item"}`;
        return `${k}: ${v}`;
      })
      .join("\n\n");
  }
  return String(conteudo);
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

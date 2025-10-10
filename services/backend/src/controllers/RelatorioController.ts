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

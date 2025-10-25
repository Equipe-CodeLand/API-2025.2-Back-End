import { Request, Response } from "express";
import { enviarEmail } from "../services/emailService";
import db from "../db/db";
import axios from 'axios';

const PLN_URL = "http://127.0.0.1:5000";

export async function enviarRelatorioPorEmail(req: Request, res: Response) {
  try {
    const { relatorioId } = req.body;
    const usuarioId = req.user?.id;

    // Buscar o relatório diretamente do banco
    const [relatorioRows]: [any[], any] = await db.query(
      `SELECT id, titulo, caminho_arquivo, criado_em 
       FROM relatorio 
       WHERE id = ? AND usuario_id = ?`,
      [relatorioId, usuarioId]
    );

    if (relatorioRows.length === 0) {
      return res.status(404).json({ error: "Relatório não encontrado" });
    }

    const relatorio = relatorioRows[0];

    // Verificar se usuário pode receber emails
    const usuario = req.user;
    if (!usuario?.receberEmails) {
      return res.status(400).json({
        error: "Usuário não autorizou recebimento de emails"
      });
    }

    // Buscar conteúdo do relatório via PLN
    let conteudoRelatorio = "";
    try {
      const response = await axios.get(`${PLN_URL}/relatorio/conteudo`, {
        params: { caminho: relatorio.caminho_arquivo }
      });
      const bruto = (response.data as any).conteudo;
      try {
        const jsonParsed = typeof bruto === "string" ? JSON.parse(bruto) : bruto;
        conteudoRelatorio = formatarConteudoRelatorio(jsonParsed);
      } catch {
        conteudoRelatorio = formatarConteudoRelatorio(bruto);
      }
    } catch (error) {
      console.error('Erro ao buscar conteúdo:', error);
      conteudoRelatorio = "Erro ao carregar conteúdo do relatório";
    }

    // Preparar e enviar email
    const dataFormatada = new Date(relatorio.criado_em).toLocaleDateString('pt-BR');
    const assunto = `${relatorio.titulo} - ${dataFormatada}`;

    const htmlContent = `
      <h2>Olá, ${usuario?.nome}!</h2>
      <p>Segue o relatório solicitado:</p>
      <h3>${relatorio.titulo}</h3>
      <p><strong>Data:</strong> ${dataFormatada}</p>
      <hr>
      <div style="white-space: pre-line; font-family: monospace; background: #f5f5f5; padding: 15px;">
        ${conteudoRelatorio}
      </div>
      <hr>
      <p><em>Este é um email automático do sistema DomRock.</em></p>
    `;

    await enviarEmail({
      to: usuario?.email || '',
      subject: assunto,
      html: htmlContent,
      attachments: [{
        filename: `${relatorio.titulo.replace(/[^a-zA-Z0-9]/g, '_')}_${dataFormatada.replace(/\//g, '-')}.txt`,
        content: conteudoRelatorio
      }]
    });

    return res.json({
      message: "Relatório enviado por email com sucesso!",
      emailEnviado: usuario?.email
    });
  } catch (error: any) {
    console.error('Erro ao enviar relatório por email:', error);
    return res.status(500).json({
      error: error.message || "Erro interno do servidor ao enviar email"
    });
  }
}

function formatarConteudoRelatorio(conteudo: any): string {
  if (Array.isArray(conteudo)) {
    return conteudo.join("\n\n");
    /* } else if (conteudo && typeof conteudo === "object" && conteudo.paragrafos) {
          return `${conteudo.titulo}\n\n${conteudo.paragrafos.join("\n\n")}`;*/
  } else if (typeof conteudo === "string") {
    return conteudo;
  } else {
    return JSON.stringify(conteudo, null, 2);
  }
}
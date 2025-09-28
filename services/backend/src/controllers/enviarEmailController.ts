import { Response } from "express";
import { AuthRequest } from "../middlewares/auth";
import { enviarEmail } from "../services/emailService";
import db from "../db/db";
import axios from 'axios';

export async function enviarRelatorioPorEmail(req: AuthRequest, res: Response) {
  try {
    const { relatorioId } = req.body;
    const usuarioId = req.user.id;

    // Buscar dados do usuário
    const [usuarioRows]: [any[], any] = await db.query(
      "SELECT nome, email, receberEmails FROM usuarios WHERE id = ?",
      [usuarioId]
    );

    if (usuarioRows.length === 0) {
      return res.status(404).json({ error: "Usuário não encontrado" });
    }

    const usuario = usuarioRows[0];

    if (!usuario.receberEmails) {
      return res.status(400).json({ 
        error: "Usuário não autorizou recebimento de emails" 
      });
    }

    // Buscar dados do relatório
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

    // Ler conteúdo do arquivo através do serviço PLN
    let conteudoRelatorio = "";
    try {
      // Usar o serviço PLN para obter o conteúdo do arquivo
      const PLN_URL = "http://127.0.0.1:5000";
      const response = await axios.get(`${PLN_URL}/relatorio/conteudo`, {
        params: { caminho: relatorio.caminho_arquivo }
      });
      
      conteudoRelatorio = response.data.conteudo;
      
      if (conteudoRelatorio === "Arquivo não encontrado") {
        throw new Error("Arquivo do relatório não encontrado no servidor PLN");
      }
    } catch (error) {
      console.error('Erro ao obter conteúdo do relatório:', error);
      conteudoRelatorio = "Erro ao carregar conteúdo do relatório";
    }

    // Preparar dados do email
    const dataFormatada = new Date(relatorio.criado_em).toLocaleDateString('pt-BR');
    const assunto = `${relatorio.titulo} - ${dataFormatada}`;
    
    const htmlContent = `
      <h2>Olá, ${usuario.nome}!</h2>
      <p>Segue em anexo o relatório solicitado:</p>
      <h3>${relatorio.titulo}</h3>
      <p><strong>Data de geração:</strong> ${dataFormatada}</p>
      <hr>
      <div style="white-space: pre-line; font-family: monospace;">
        ${conteudoRelatorio}
      </div>
      <hr>
      <p><em>Este é um email automático do sistema DomRock.</em></p>
    `;

    // Enviar email
    await enviarEmail({
      to: usuario.email,
      subject: assunto,
      html: htmlContent,
      attachments: [{
        filename: `${relatorio.titulo}_${dataFormatada}.txt`,
        content: conteudoRelatorio
      }]
    });

    return res.json({ 
      message: "Relatório enviado por email com sucesso!",
      emailEnviado: usuario.email 
    });

  } catch (error: any) {
    console.error('Erro ao enviar relatório por email:', error);
    return res.status(500).json({ 
      error: "Erro interno do servidor ao enviar email" 
    });
  }
}
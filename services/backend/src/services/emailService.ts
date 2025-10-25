import nodemailer from 'nodemailer';
import dotenv from 'dotenv';

dotenv.config();

// Verificar credenciais na inicialização
if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) {
  console.error('⚠️  EMAIL_USER e EMAIL_PASSWORD devem estar no .env');
}

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD
  }
});

export interface EmailData {
  to: string;
  subject: string;
  html: string;
  attachments?: Array<{
    filename: string;
    content: string;
  }>;
}

export async function enviarEmail(emailData: EmailData): Promise<void> {
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) {
    throw new Error('Configurações de email não encontradas');
  }

  try {
    // Testar conexão
    await transporter.verify();
    
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: emailData.to,
      subject: emailData.subject,
      html: emailData.html,
      attachments: emailData.attachments
    });
    
    console.log('✅ Email enviado para:', emailData.to);
  } catch (error) {
    console.error('❌ Erro ao enviar email:', error);
    throw new Error('Falha ao enviar email: ' + (error as Error).message);
  }
}
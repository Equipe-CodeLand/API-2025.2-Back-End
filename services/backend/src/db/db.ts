import mysql from "mysql2/promise";
import dotenv from "dotenv";

dotenv.config();

const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  connectTimeout: 30000, // 30 segundos
});

// Teste de conexão
db.getConnection()
  .then(() => console.log("Conexão ao banco bem-sucedida!"))
  .catch((err) => console.error("Erro na conexão ao banco:", err.stack));

export default db;

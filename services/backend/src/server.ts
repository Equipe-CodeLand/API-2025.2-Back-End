import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { connectDB, sequelize } from "./db/db";
import authRoutes from "./routes/auth";
import usuarioRoutes from "./routes/usuario"

dotenv.config();

const app = express();

// Configurar CORS
app.use(cors({
  origin: "http://localhost:3000", 
  credentials: true
}));

app.use(express.json());

app.use("/auth", authRoutes);
app.use(usuarioRoutes)

const PORT = process.env.PORT || 4000;

const startServer = async () => {
  await connectDB();

  await sequelize.sync({ alter: true });

  app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));
};

startServer();
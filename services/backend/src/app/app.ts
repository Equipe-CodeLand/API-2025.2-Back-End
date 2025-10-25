import express from "express";
import router from "../routes/rotas";
import dotenv from "dotenv";
import cors from "cors"; 

dotenv.config();

const app = express();
app.use(
  cors({
    origin: "http://localhost:3000", 
    methods: ["GET", "POST", "PUT", "DELETE"], 
    allowedHeaders: ["Content-Type", "Authorization"], 
  }),
);

app.use(express.json());

app.use("/api", router); // Prefixo /api 

const PORT = process.env.PORT || 4000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Servidor rodando em http://0.0.0.0:${PORT}`);
});

export default app;

import { DataTypes, Model } from "sequelize";
import sequelize from "../db/db";
import { Usuario } from "./Usuario";

export class Mensagem extends Model {
  public id!: number;
  public usuario_id!: number;
  public conteudo!: string;
  public tipo!: "usuario" | "bot"; // quem enviou
}

Mensagem.init(
  {
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
    },
    usuario_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
      references: { model: "usuarios", key: "id" },
    },
    conteudo: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    tipo: {
      type: DataTypes.ENUM("usuario", "bot"),
      allowNull: false,
    },
  },
  {
    sequelize,
    tableName: "mensagens",
  }
);

import { DataTypes, Model } from "sequelize";
import { sequelize } from "../db/db";
import { Status } from "../enum/Status";

export class Usuario extends Model {
  public id!: number;
  public nome!: string;
  public status!: string;
  public username!: string;
  public password!: string;
  public cargo!: string;
  public receberEmails!: boolean;
}

Usuario.init(
  {
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
    },
    nome: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    status: {
      type: DataTypes.STRING(20),
      allowNull: false,
      defaultValue: Status.ATIVO,
    },
    email: {
      type: DataTypes.STRING(100),
      allowNull: false,
      unique: true,
    },
    password: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
      cargo: {
      type: DataTypes.STRING(50),
      allowNull: false,
    },
    receberEmails: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      defaultValue: true,
    },
  },
  {
    sequelize,
    tableName: "usuarios",
  }
);
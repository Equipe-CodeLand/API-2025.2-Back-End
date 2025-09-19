import { DataTypes, Model } from "sequelize";
import { sequelize } from "../db/db";
import { Status } from "../enum/Status";

export class Usuario extends Model {
  public id!: number;
  public nome!: string;
  public status!: string;
  public username!: string;
  public password!: string;
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
      allowNull: true, // Mudei para true ou remova se não precisar
    },
    status: {
      type: DataTypes.STRING(20),
      allowNull: false,
      defaultValue: Status.ATIVO,
    },
    username: {
      type: DataTypes.STRING(100),
      allowNull: false,
      unique: true,
    },
    password: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
  },
  {
    sequelize,
    tableName: "usuarios",
  }
);
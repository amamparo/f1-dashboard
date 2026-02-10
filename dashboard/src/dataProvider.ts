import simpleRestProvider from "ra-data-simple-rest";
import { API_BASE_URL } from "./utils/common";

export const dataProvider = simpleRestProvider(API_BASE_URL);

import crypto from "crypto";
import { supabase } from "./supabase.js";

const PASSWORD_HASH_ITERATIONS = 310000;

function hashPassword(password, saltHex) {
  const salt = saltHex
    ? Buffer.from(saltHex, "hex")
    : crypto.randomBytes(16);

  const hash = crypto.pbkdf2Sync(
    password,
    salt,
    PASSWORD_HASH_ITERATIONS,
    32,
    "sha256"
  );

  return {
    passwordHash: hash.toString("hex"),
    passwordSalt: salt.toString("hex"),
  };
}

function cleanFarmer(farmer) {
  if (!farmer) return null;

  const {
    password_hash,
    password_salt,
    password,
    ...safeFarmer
  } = farmer;

  return safeFarmer;
}

export async function registerFarmerSupabase(account) {
  const { passwordHash, passwordSalt } = hashPassword(account.password);

  const { data, error } = await supabase
    .from("farmers")
    .insert({
      name: account.name.trim(),
      password_hash: passwordHash,
      password_salt: passwordSalt,
      crop: account.crop.trim(),
      soil_type: account.soil_type.trim(),
      planting_date: account.planting_date,
      place_name: account.place_name.trim(),
      pincode: account.pincode.trim(),
    })
    .select()
    .single();

  if (error) {
    if (error.code === "23505") {
      return null;
    }

    throw new Error(`Supabase registration failed: ${error.message}`);
  }

  return cleanFarmer(data);
}

export async function loginFarmerSupabase(name, password) {
  const { data, error } = await supabase
    .from("farmers")
    .select("*")
    .ilike("name", name.trim())
    .limit(1)
    .maybeSingle();

  if (error) {
    throw new Error(`Supabase login lookup failed: ${error.message}`);
  }

  if (!data) {
    return null;
  }

  const { passwordHash } = hashPassword(password, data.password_salt);

  if (
    !crypto.timingSafeEqual(
      Buffer.from(passwordHash, "hex"),
      Buffer.from(data.password_hash, "hex")
    )
  ) {
    return null;
  }

  return cleanFarmer(data);
}

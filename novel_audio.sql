/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80022
 Source Host           : localhost:3306
 Source Schema         : novel_audio

 Target Server Type    : MySQL
 Target Server Version : 80022
 File Encoding         : 65001

 Date: 04/03/2021 08:50:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chapter
-- ----------------------------
DROP TABLE IF EXISTS `chapter`;
CREATE TABLE `chapter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `num` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `url` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Table structure for novel
-- ----------------------------
DROP TABLE IF EXISTS `novel`;
CREATE TABLE `novel` (
  `id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `img` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tags` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `author` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `audio_author` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `intro` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` varchar(1) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET FOREIGN_KEY_CHECKS = 1;

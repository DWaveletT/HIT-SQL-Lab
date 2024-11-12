-- 使用utf8mb4字符集，确保支持多语言字符集
CREATE DATABASE IF NOT EXISTS university CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

DROP DATABASE IF EXISTS university;
CREATE DATABASE university;

USE university;

DROP TABLE IF EXISTS Course_Room;
DROP TABLE IF EXISTS Course_Book;
DROP TABLE IF EXISTS Book;
DROP TABLE IF EXISTS Term;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Enrollment;
DROP TABLE IF EXISTS Class;
DROP TABLE IF EXISTS Teacher;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Course;

-- 学生表
CREATE TABLE Student (
    SID INT PRIMARY KEY AUTO_INCREMENT,  -- 学生 ID
    SName VARCHAR(100) NOT NULL,         -- 学生名
    SGender ENUM('M', 'F') NOT NULL,     -- 性别（M 代表男，F 代表女）
    GID INT                              -- 班级 ID（外键）
);

-- 课程表
CREATE TABLE Course (
    CID INT PRIMARY KEY AUTO_INCREMENT,  -- 课程 ID
    CName VARCHAR(100) NOT NULL,         -- 课程名
    Credits INT NOT NULL,                -- 学分
    DID INT                           -- 学期 ID（外键）
);

-- 选课表
CREATE TABLE Enrollment (
    SID INT,                             -- 学生 ID（外键）
    CID INT,                             -- 课程 ID（外键）
    Score INT,                           -- 分数
    PRIMARY KEY (SID, CID),              -- 联合主键
    FOREIGN KEY (SID) REFERENCES Student(SID) ON DELETE CASCADE,   -- 外键引用 Student 表
    FOREIGN KEY (CID) REFERENCES Course(CID) ON DELETE CASCADE     -- 外键引用 Course 表
);

-- 教材表
CREATE TABLE Book (
    BID INT PRIMARY KEY AUTO_INCREMENT,  -- 教材 ID
    BName VARCHAR(100) NOT NULL          -- 教材名称
);

-- 课程与教材的关联表
CREATE TABLE Course_Book (
    CID INT,                             -- 课程 ID（外键）
    BID INT,                             -- 教材 ID（外键）
    PRIMARY KEY (CID, BID),              -- 联合主键
    FOREIGN KEY (CID) REFERENCES Course(CID) ON DELETE CASCADE,    -- 外键引用 Course 表
    FOREIGN KEY (BID) REFERENCES Book(BID) ON DELETE CASCADE       -- 外键引用 Book 表
);

-- 教师表
CREATE TABLE Teacher (
    TID INT PRIMARY KEY AUTO_INCREMENT,  -- 教师 ID
    TName VARCHAR(100) NOT NULL          -- 教师姓名
);

-- 班级表
CREATE TABLE Class (
    GID INT PRIMARY KEY AUTO_INCREMENT,  -- 班级 ID
    GName VARCHAR(100) NOT NULL,         -- 班级名称
    TID INT,                             -- 教师 ID
    FOREIGN KEY (TID) REFERENCES Teacher(TID) ON DELETE SET NULL   -- 外键引用 Teacher 表
);

-- 学期表
CREATE TABLE Term (
    DID INT PRIMARY KEY AUTO_INCREMENT,  -- 学期 ID
    DName VARCHAR(100) NOT NULL,         -- 学期名称
    STime DATE NOT NULL,                 -- 学期开始日期
    ETime DATE NOT NULL                  -- 学期结束日期
);

-- 教室表
CREATE TABLE Room (
    RID INT PRIMARY KEY AUTO_INCREMENT,  -- 教室号，主键，自增
    RName VARCHAR(100) NOT NULL          -- 教室名称
);

-- 课程与教室的关联表，表示课程在某教室上课，并包含上课时间
CREATE TABLE Course_Room (
    CID INT,                             -- 课程ID（外键）
    RID INT,                             -- 教室ID（外键）
    ClassTime TIME NOT NULL,             -- 上课时间
    PRIMARY KEY (CID, RID),              -- 联合主键
    FOREIGN KEY (CID) REFERENCES Course(CID) ON DELETE CASCADE,    -- 外键引用Course表
    FOREIGN KEY (RID) REFERENCES Room(RID) ON DELETE CASCADE       -- 外键引用Room表
);

-- 插入一些测试数据
INSERT INTO Student (SName, SGender, GID) VALUES
    ('Reimu',     'F', 1),
    ('Marisa',    'F', 1),
    ('Cirno',     'F', 1),
    ('Meirin',    'F', 2),
    ('Patchouli', 'F', 2),
    ('Sakuya',    'F', 2),
    ('Remilia',   'F', 2),
    ('Furandre',  'F', 2);

INSERT INTO Course (CName, Credits, DID) VALUES
    ('语文', 3, 1),
    ('数学', 5, 1),
    ('物理', 5, 1),
    ('化学', 4, 2),
    ('生物', 4, 2),
    ('历史', 3, 3),
    ('政治', 3, 3),
    ('地理', 4, 3);

INSERT INTO Enrollment (SID, CID, Score) VALUES
    (1, 1, 91),
    (1, 2, 92),
    (1, 3, 93),
    (1, 4, 94),
    (1, 5, 95),
    (1, 6, 96),
    (1, 7, 97),
    (1, 8, 98),
    (2, 1, 51),
    (2, 2, 52),
    (2, 3, 53),
    (2, 4, 54),
    (2, 5, 55),
    (2, 6, 56),
    (2, 7, 57),
    (2, 8, 58),
    (3, 2, 9);
INSERT INTO Book (BName) VALUES
    ('语文书（上册）'),
    ('语文书（下册）'),
    ('具体数学'),
    ('近世代数'),
    ('实变函数'),
    ('复变函数'),
    ('集合论'),
    ('图论'),
    ('物理书'),
    ('化学书'),
    ('生物书'),
    ('历史书'),
    ('政治书'),
    ('地理书');
INSERT INTO Course_Book (CID, BID) VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (2, 8),
    (3, 9),
    (4, 10),
    (5, 11),
    (6, 12),
    (7, 13),
    (8, 14);

INSERT INTO Teacher (TName) VALUES
    ('上白泽慧音'),
    ('本居小铃');
INSERT INTO Class (GName, TID) VALUES
    ('1 班', 1),
    ('2 班', 2);
INSERT INTO Term (DName, STime, ETime) VALUES
    ('2022 年', '2022-09-01', '2023-07-01'),
    ('2023 年', '2023-09-01', '2024-07-01'),
    ('2024 年', '2024-09-01', '2025-07-01'),
    ('2025 年', '2025-09-01', '2026-07-01');
INSERT INTO Room (RName) VALUES
    ('一班'),
    ('二班');
INSERT INTO Course_Room (CID, RID, ClassTime) VALUES
    (1, 1, '08:00:00'),
    (1, 2, '10:00:00'),
    (2, 1, '13:45:00'),
    (2, 2, '15:45:00');

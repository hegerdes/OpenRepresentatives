# SQL commands for table creation:

## Queries
```SQL
# Most missing persons
SELECT DISTINCT m.resid, m.f_name, m.s_name , p.party ,
COUNT(m.resid) OVER (PARTITION BY m.resid) as misses
from missing m  inner join parliaments p on m.resid = p.resid
order by misses desc ;
```


## Tables

### Head
```SQL
CREATE TABLE head (
	headID INT NOT NULL,
	session INT NOT NULL,
	period INT NOT NULL,
	publisher VARCHAR(64) DEFAULT 'Deutscher Bundestag',
	type VARCHAR(64) DEFAULT 'Stenografischer Bericht',
	title VARCHAR(64) DEFAULT '',
	place VARCHAR(64) DEFAULT 'Berlin',
	date DATE,
	url VARCHAR(265) DEFAULT '',
	PRIMARY KEY (headID)
);
```


### Content
```SQL
CREATE TABLE content (
	contentID SERIAL,
	sessionID INT NOT NULL,
	title VARCHAR(1024) NOT NULL,
	topic VARCHAR(4096) NOT NULL,
	PRIMARY KEY (contentID),
	FOREIGN KEY (sessionID) REFERENCES head(headID)
);
```

### Parliament
```SQL
CREATE TABLE parliaments (
	resID BIGINT NOT NULL,
	f_name VARCHAR(64),
	s_name VARCHAR(64),
	party VARCHAR(64),
	roll VARCHAR(128) DEFAULT 'none',
	PRIMARY KEY (resID)
);
```

### Docs
```SQL
CREATE TABLE docs (
	docID SERIAL,
	contentID INT,
	sessionID INT,
	docName VARCHAR(16) NOT NULL,
	PRIMARY KEY (docID),
	FOREIGN KEY (sessionID) REFERENCES head(headID),
	FOREIGN KEY (contentID) REFERENCES content(contentID)
);
```

### Missing
```SQL
CREATE TABLE missing (
	missingID SERIAL,
	resID INT NOT NULL,
	sessionID INT NOT NULL,
	f_name VARCHAR(64) NOT NULL,
	s_name VARCHAR(64) NOT NULL,
	PRIMARY KEY (missingID),
	FOREIGN KEY (resID) REFERENCES parliaments(resID),
	FOREIGN KEY (sessionID) REFERENCES head(headID)
);
```


### Comments
```SQL
CREATE TABLE comments (
	commentID BIGINT NOT NULL,
	type VARCHAR(32) DEFAULT 'kommentar',
	content VARCHAR(4096) DEFAULT 'none',
	PRIMARY KEY (commentID)
);
```

### Talks
```SQL
CREATE TABLE talks (
	talkID BIGINT NOT NULL,
	speakerID BIGINT NOT NULL,
	speakerName VARCHAR(128) NOT NULL,
	contentID INT NOT NULL,
	sessionID INT NOT NULL,
	talk TEXT NOT NULL,
	PRIMARY KEY (talkID),
	FOREIGN KEY (speakerID) REFERENCES parliaments(resID),
	FOREIGN KEY (sessionID) REFERENCES head(headID),
	FOREIGN KEY (contentID) REFERENCES content(contentID)
);
```

### Talk_Com
 ```SQL
CREATE TABLE talk_com (
	ID SERIAL,
	talkID BIGINT NOT NULL,
	commentID BIGINT NOT NULL,
	PRIMARY KEY (ID),
	FOREIGN KEY (commentID) REFERENCES comments(commentID),
	FOREIGN KEY (talkID) REFERENCES talks(talkID)
);
```

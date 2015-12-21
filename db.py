import pyodbc
from datetime import datetime, timedelta

def Tracks_db_conn():
    cnxn = pyodbc.connect(r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=TracksArtist;' +
            r'UID=rsoi;PWD=Aa123456')
    cursor = cnxn.cursor()
    return cursor;

def users_db_conn():
    cnxn = pyodbc.connect(r'DRIVER={SQL Server};' +
            r'SERVER=(local)\SQLEXPRESS;' +
            r'Database=rsoi;' +
            r'UID=rsoi;PWD=Aa123456')
    cursor = cnxn.cursor()
    return cursor;

def user_exist(username):
    cursor = users_db_conn()
    cursor.execute("select * from Users where UserName='" + username+"'")
    row = cursor.fetchone()
    if row:
        return 1
    else:
        return 0

def client_exist(client_id):
    cursor = users_db_conn()
    cursor.execute("select * from Apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row:
        return 1
    else:
        return 0

def insert_user(username, first_name, last_name, tel, email, password):
    db = users_db_conn()
    insert_str  = ("insert into Users"+
                       " (UserName, FirstName, LastName, Telephone, Email, Password)"+
                       " values ('%s','%s','%s','%s','%s','%s' )"
                       % (username, first_name, last_name, tel, email, password))
    db.execute(insert_str)
    db.commit()
    return 0;

def len_db():
    cursor = Tracks_db_conn()
    cursor.execute("select count(*) from ")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0;

def Tracks_from_db(page, per_page):
    items = []
    cursor = Tracks_db_conn()
    cursor.execute("select * from ")
    rows = cursor.fetchall()
    i = 0
    for row in rows:
        if i < page * per_page:
            text = row.title.decode(encoding='ISO-8859-1', errors='strict')
            items.append({
            #'Artist': row.Artist,
            'ArtistId': row.ArtistId,
            'Album': row.Album,
            'Year': row.Year,
            'Genre':row.Genre
            })
            i += 1
        if i >= (page + 1) * per_page:
            i += 1
            break
    return items;

def film_by_id(id):
    cursor = Tracks_db_conn()
    cursor.execute("select * from dbo.main where id=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def len_db_dirs():
    count = 0;
    cursor = Tracks_db_conn()
    cursor.execute("select * from dbo.directors")
    cursor1= Tracks_db_conn()
    cursor1.execute("select * from dbo.main")
    rows = cursor.fetchall()
    rows1 = cursor1.fetchall()
    for row in rows:
        for row1 in rows1:
            if row1.id_director==row.id_director:
                count += 1
    return count;

def artist_from_db(page, per_page):
    cursor = Tracks_db_conn()
    cursor.execute("select * from dbo.directors")
    cursor1 = Tracks_db_conn()
    cursor1.execute("select * from dbo.main")
    rows = cursor.fetchall()
    rows1 = cursor1.fetchall()
    i = 0
    items= []
    for row1 in rows1:
        for row in rows:
            if row1.id_director==row.id_director:
                if i < page * per_page:
                    items.append({
                    'id_director': row.id_director,
                    'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
                    'title': row1.title.decode(encoding='ISO-8859-1', errors='strict'),
                    })
                    i += 1
                if i >= (page + 1) * per_page:
                    i += 1
                    break
    return items;

def director_by_id(id):
    cursor = Tracks_db_conn()
    cursor.execute("select * from dbo.directors where id_director=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def insert_track(Track, ArtistId, Album, Year, Genre):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("insert into dbo.main values ("+id+", "+id_director+",'"+title+"','"+duration+"', "+year+", '"+genre+"', "+kinopoisk_rating+")")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def insert_director(id, name, birthday, country):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("insert into dbo.directors values ("+id+", '"+name+"', '"+birthday+"', '"+country+"')")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_director(id, str, value):
    cursor = Tracks_db_conn()
    try:
        cursor.execute("update dbo.directors set "+str+"='"+value+"' where id_director="+id)
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_film(id, str, value):
    cursor = Tracks_db_conn()
    try:
        if str == 'title' or str == 'duration' or str == 'genre':
            cursor.execute("update dbo.main set "+str+"='"+value+"' where id="+id)
            cursor.commit()
        else:
            cursor.execute("update dbo.main set "+str+"="+value+" where id="+id)
            cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def del_film(id):
    cursor = Tracks_db_conn()
    cursor.execute("delete from dbo.main where id="+id)
    cursor.commit()


###########################
def read_redirect(client_id):
    cursor = users_db_conn()
    cursor.execute("select * from Apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row:
        return row.redirect_uri
    return 0;

def user_pass_check(username, password):
    db = users_db_conn()
    select_str =("select count(*) as num from Users"+
                 " where UserName = '%s' and Password = '%s'"
               % (username, password))
    cursor = db.execute(select_str)
    row = cursor.fetchone()
    if row.num == 0:
        return 0
    return 1;

def code_insert(code, username):
    try:
        cursor = users_db_conn()
        cursor.execute("update AppCodes set code='"+code+"' where UserName='" + username+"'")
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1;

def client_secret_check(client_id, secret_id):
    cursor = users_db_conn()
    cursor.execute("select * from Apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row.secret_id.find(secret_id)!=-1:
        return 1
    return 0;

def code_check(code):
    cursor = users_db_conn()
    cursor.execute("select * from AppCodes where Code='" + code+"'")
    row = cursor.fetchone()
    if row:
        return row.phone
    return 0;

def refresh_token_check(refresh_token):
    cursor = users_db_conn()
    cursor.execute("select * from Tokens where RefreshToken='" + refresh_token+"'")
    row = cursor.fetchone()
    if row:
        return row.UserName
    return 0;

def insert_token(user_name, access_token, expire_time, refresh_token):
    cursor = users_db_conn()
    cursor.execute("update Tokens set RefreshToken='"+refresh_token+"' where UserName='" + user_name+"'")
    cursor.execute("update Tokens set AccessToken='"+access_token+"' where UserName='" + user_name+"'")
    cursor.execute("update Tokens set Expires='"+str(expire_time)+"' where UserName='" + user_name+"'")
    cursor.commit()
    return 1;

def expired_check(refresh_token):
    cursor = users_db_conn()
    print refresh_token
    cursor.execute("select * from Tokens where RefreshToken='" + refresh_token+"'")
    row = cursor.fetchone()
    if row:
        print datetime.now()
        if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            return 2
        if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
            return 1
    return 0

def expired_check1(access_token):
    cursor = users_db_conn()
    cursor.execute("select * from Tokens where AccessToken='" + access_token+"'")
    row = cursor.fetchone()
    time30 = timedelta(minutes=0)
    if row:
        print datetime.now()
        try:
            if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')-datetime.now() > time30:
                print datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')
                return 2
            if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')-datetime.now() < time30:
                return 1
        except TypeError:
            return 2
    return 0

def expired_refresh(refresh_token):
    cursor = users_db_conn()
    expire_time = datetime.now() + timedelta(minutes=10)
    cursor.execute("update Tokens set expires='"+str(expire_time)+"' where RefreshToken='" + refresh_token+"'")
    cursor.commit()
    return 1;

def get_me(access_token):
    cursor = users_db_conn()
    cursor.execute("select UserName from Tokens where AccessToken='" + access_token+"'")
    row = cursor.fetchone()
    
    if row:
        username = row.UserName
        DB = users_db_conn()
        select_str = ("select "+
                  "UserName,FirstName,LastName,Telephone,Email "+
                  "from Users where UserName = '%s'" % username)
        cursor = DB.execute(select_str)
        row = cursor.fetchone()
        if not row:
            return None
        return row 
